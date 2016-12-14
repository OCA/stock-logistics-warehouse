# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, exceptions, fields, models, _
import time


class ProductInventoryAccountReconcile(models.TransientModel):
    _name = 'product.inventory.account.reconcile'

    @api.model
    def _default_journal(self):
        res = self.env['account.journal'].search([('type', '=', 'general')])
        return res and res[0] or False

    increase_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Valuation Increase Contra-Account')
    decrease_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Valuation Decrease Contra-Account')
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 default=_default_journal)
    remarks = fields.Text('Remarks', help="This text is copied to the "
                                          "journal entry.")

    @api.model
    def _prepare_move_data(self, date_move):

        period = self.env['account.period'].find(date_move)[0]

        return {
            'narration': self.remarks,
            'date': date_move,
            'ref': 'Inventory valuation reconciliation',
            'journal_id': self.journal_id.id,
            'period_id': period.id,
        }

    @api.model
    def _prepare_debit_move_line_data(self, move, amount, account_id, prod,
                                      date_move):
        return {
            'name': prod.name,
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
            'name': prod.name,
            'date': date_move,
            'product_id': prod.id,
            'account_id': account_id,
            'move_id': move.id,
            'credit': amount
        }

    @api.multi
    def create_accounting_entries(self):
        context = self._context or {}
        active_model = self.env.context['active_model']
        if active_model == 'product.product':
            products = self.env['product.product'].browse(
                context.get('active_ids', []))
            for product in products:
                if product.valuation != 'real_time':
                    raise exceptions.Warning(
                        _('Product %s must have real time '
                          'valuation') % product.name)
        elif active_model == 'product.template':
            templates = self.env['product.template'].browse(
                context.get('active_ids', []))
            for template in templates:
                if template.valuation != 'real_time':
                    raise exceptions.Warning(
                        _('Product Template %s must have real time '
                          'valuation') % template.name)
            products = templates.mapped('product_variant_ids')
        else:
            raise exceptions.Warning(
                _('Incorrect model.'))
        move_ids = []
        timenow = time.strftime('%Y-%m-%d')
        for product in products:
            if not product.valuation_discrepancy:
                continue
            move_data = self._prepare_move_data(timenow)
            datas = self.env['product.template'].get_product_accounts(
                product.product_tmpl_id.id)
            move = self.env['account.move'].create(move_data)
            if product.valuation_discrepancy <= 0.0:
                debit_account_id = self.decrease_account_id.id
                credit_account_id = \
                    datas['property_stock_valuation_account_id']
            else:
                debit_account_id = \
                    datas['property_stock_valuation_account_id']
                credit_account_id = self.increase_account_id.id
            move_line_data = self._prepare_debit_move_line_data(
                move, abs(product.valuation_discrepancy), debit_account_id,
                product, timenow)
            self.env['account.move.line'].create(move_line_data)
            move_line_data = self._prepare_credit_move_line_data(
                move, abs(product.valuation_discrepancy), credit_account_id,
                product, timenow)
            self.env['account.move.line'].create(move_line_data)
            if move.journal_id.entry_posted:
                move.post()
            move_ids.append(move.id)

        return {
            'domain': [('id', 'in', move_ids)],
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window'
        }
