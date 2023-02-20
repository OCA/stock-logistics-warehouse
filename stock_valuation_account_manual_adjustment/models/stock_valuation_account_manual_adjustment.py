# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision('Account')


class StockValuationAccountManualAdjustment(models.Model):
    _name = 'stock.valuation.account.manual.adjustment'
    _description = 'Stock Valuation Account Manual Adjustment'

    @api.model
    def _default_journal(self):
        return self.env['account.journal'].search(
            [('type', '=', 'general')], limit=1)

    name = fields.Char(
        string='Reference',
        help="Reference for the journal entry", readonly=True,
        required=True, states={'draft': [('readonly', False)]},
        copy=False, default='/')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
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
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    decrease_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Valuation Decrease Contra-Account',
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Journal', readonly=True,
        default=_default_journal, required=True,
        states={'draft': [('readonly', False)]})
    remarks = fields.Text(
        string='Remarks',
        help="This text is copied to the journal entry.",
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection(
        string='Status', selection=[('draft', 'Draft'), ('posted', 'Posted')],
        required=True, default='draft', readonly=False)
    amount = fields.Float(
        string="Adjustment amount", digits=UNIT,
        readonly=True, required=True,
        states={'done': [('readonly', False)]})
    document_date = fields.Date(
        string='Creation date', required=True, readonly=True,
        default=lambda self: fields.Date.context_today(self),
        states={'draft': [('readonly', False)]})
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Created by', readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user)
    post_date = fields.Datetime(
        string='Posting Date', readonly=True,
        states={'draft': [('readonly', False)]},
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
                self.product_id.categ_id and \
                self.product_id.categ_id.with_context(
                    force_company=self.env.user.company_id.id).\
                property_inventory_revaluation_increase_account_categ
            self.decrease_account_id = self.product_id.categ_id and \
                self.product_id.categ_id.with_context(
                    force_company=self.env.user.company_id.id).\
                property_inventory_revaluation_decrease_account_categ

    def _prepare_move_data(self, date_move, debit_move_line_data,
                           credit_move_line_data):
        self.ensure_one()
        line_data = ([(0, 0, debit_move_line_data)] +
                     [(0, 0, credit_move_line_data)])
        return {
            'narration': self.remarks,
            'date': date_move,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'stock_valuation_account_manual_adjustment_id': self.id,
            'line_ids': line_data
        }

    def _prepare_debit_move_line_data(self, amount, account_id, prod,
                                      date_move):
        self.ensure_one()
        return {
            'name': '(%s) %s' % (self.name, prod.name),
            'date': date_move,
            'product_id': prod.id,
            'account_id': account_id,
            'debit': amount
        }

    def _prepare_credit_move_line_data(self, amount, account_id,
                                       prod, date_move):
        self.ensure_one()
        return {
            'name': '(%s) %s' % (self.name, prod.name),
            'date': date_move,
            'product_id': prod.id,
            'account_id': account_id,
            'credit': amount
        }

    @api.multi
    def post(self):
        today = fields.Date.today()
        for adj in self:
            if not adj.amount:
                continue
            datas = adj.product_id.product_tmpl_id.with_context(
                force_company=self.env.user.company_id.id).get_product_accounts()

            if self.env.context.get('valuation_discrepancy', False):
                valuation_discrepancy = self.env.context.get(
                    'valuation_discrepancy')
            else:
                valuation_discrepancy = adj.product_id.valuation_discrepancy

            if valuation_discrepancy <= 0.0:
                debit_account_id = self.decrease_account_id.id
                if not self.increase_account_id:
                    credit_account_id = \
                        datas['stock_valuation'].id or False
                else:
                    credit_account_id = self.increase_account_id.id
            else:
                if not self.decrease_account_id:
                    debit_account_id = \
                        datas['stock_valuation'].id or False
                else:
                    debit_account_id = self.decrease_account_id.id
                credit_account_id = self.increase_account_id.id

            debit_move_line_data = self._prepare_debit_move_line_data(
                abs(valuation_discrepancy),
                debit_account_id, adj.product_id, today)
            credit_move_line_data = self._prepare_credit_move_line_data(
                abs(valuation_discrepancy),
                credit_account_id, adj.product_id, today)

            move_data = self._prepare_move_data(
                today, debit_move_line_data, credit_move_line_data)
            move = self.env['account.move'].create(move_data)

            move.post()
            self.post_date = fields.Datetime.now()
            self.state = 'posted'

    @api.model
    def create(self, values):
        if values.get('name', '/') == '/':
            values['name'] = self.env['ir.sequence'].next_by_code(
                'stock.valuation.account.manual')
        return super(StockValuationAccountManualAdjustment,
                     self).create(values)
