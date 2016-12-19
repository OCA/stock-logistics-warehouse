# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.addons import decimal_precision as dp
import time
UNIT = dp.get_precision('Account')


class StockValuationAccountManualAdjustment(models.Model):

    _name = 'stock.valuation.account.manual.adjustment'
    _description = 'Stock Valuation Account Manual Adjustment'

    @api.model
    def _default_journal(self):
        res = self.env['account.journal'].search([('type', '=', 'general')])
        return res and res[0] or False

    name = fields.Char('Reference',
                       help="Reference for the journal entry",
                       required=True, states={'done': [('readonly', True)]},
                       copy=False, default='/')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        states={'done': [('readonly', True)]},
        domain=[('valuation', '=', 'real_time')])
    inventory_value = fields.Float(
        string='Inventory Value', related='product_id.inventory_value',
        readonly=True)
    accounting_value = fields.Float(
        string='Accounting Value', related='product_id.accounting_value',
        readonly=True)
    valuation_discrepancy = fields.Float(
        string='Valuation discrepancy',
        related='product_id.valuation_discrepancy',
        readonly=True)
    increase_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Valuation Increase Contra-Account',
        required=True,
        states={'done': [('readonly', True)]})
    decrease_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Valuation Decrease Contra-Account',
        required=True,
        default='draft',
        states={'done': [('readonly', True)]})
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 default=_default_journal, required=True,
                                 states={'done': [('readonly', True)]})
    remarks = fields.Text('Remarks',
                          help="This text is copied to the journal entry.",
                          required=True, states={'done': [('readonly', True)]})
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('posted', 'Posted')], string='Status',
                             required=True, default='draft',
                             states={'done': [('readonly', True)]})
    amount = fields.Float(string="Adjustment amount", digits=UNIT,
                          required=True, states={'done': [('readonly', True)]})
    document_date = fields.Date(
        'Creation date', required=True, readonly=True,
        default=lambda self: fields.Date.context_today(self))
    user_id = fields.Many2one('res.users', 'Created by',
                              readonly=True,
                              states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user)
    post_date = fields.Datetime(
        'Posting Date', states={'done': [('readonly', True)]},
        help="Date of actual processing")

    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='stock_valuation_account_manual_adjustment_id',
        readonly=True)

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.inventory.revaluation'),
        states={'draft': [('readonly', False)]})

    @api.multi
    def button_post(self):
        self.post()
        return True

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.increase_account_id = \
                self.product_id.categ_id and self.product_id.categ_id.\
                property_inventory_revaluation_increase_account_categ
            self.decrease_account_id = self.product_id.categ_id and \
                self.product_id.categ_id.\
                property_inventory_revaluation_decrease_account_categ

    @api.model
    def _prepare_move_data(self, date_move):

        period = self.env['account.period'].find(date_move)[0]

        return {
            'narration': self.remarks,
            'date': date_move,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'period_id': period.id,
            'stock_valuation_account_manual_adjustment_id': self.id
        }

    @api.model
    def _prepare_debit_move_line_data(self, move, amount, account_id, prod,
                                      date_move):
        return {
            'name': '(%s) %s' % (self.name, prod.name),
            'date': date_move,
            'product_id': prod.id,
            'account_id': account_id,
            'move_id': move.id,
            'debit': amount
        }

    @api.model
    def _prepare_credit_move_line_data(self, move, amount, account_id,
                                       prod,
                                       date_move):
        return {
            'name': '(%s) %s' % (self.name, prod.name),
            'date': date_move,
            'product_id': prod.id,
            'account_id': account_id,
            'move_id': move.id,
            'credit': amount
        }

    @api.multi
    def post(self):
        timenow = time.strftime('%Y-%m-%d')
        for adj in self:
            if not adj.amount:
                continue
            move_data = self._prepare_move_data(timenow)
            datas = self.env['product.template'].get_product_accounts(
                adj.product_id.product_tmpl_id.id)
            move = self.env['account.move'].create(move_data)
            if adj.product_id.valuation_discrepancy <= 0.0:
                debit_account_id = self.decrease_account_id.id
                credit_account_id = \
                    datas['property_stock_valuation_account_id']
            else:
                debit_account_id = \
                    datas['property_stock_valuation_account_id']
                credit_account_id = self.increase_account_id.id
            move_line_data = self._prepare_debit_move_line_data(
                move, abs(adj.product_id.valuation_discrepancy),
                debit_account_id, adj.product_id, timenow)
            self.env['account.move.line'].create(move_line_data)
            move_line_data = self._prepare_credit_move_line_data(
                move, abs(adj.product_id.valuation_discrepancy),
                credit_account_id, adj.product_id, timenow)
            self.env['account.move.line'].create(move_line_data)
            if move.journal_id.entry_posted:
                move.post()
            self.post_date = fields.Datetime.now()
            self.state = 'posted'

    @api.model
    def create(self, values):
        sequence_obj = self.env['ir.sequence']
        if values.get('name', '/') == '/':
            values['name'] = \
                sequence_obj.get('stock.valuation.account.manual')
        return super(StockValuationAccountManualAdjustment,
                     self).create(values)
