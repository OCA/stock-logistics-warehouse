# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, exceptions, fields, models, _


class StockValuationAccountMassAdjust(models.TransientModel):
    _name = 'stock.valuation.account.mass.adjust'
    _description = 'Mass Adjust Stock Valuation Account Discrepancies'

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
                                          "journal entry.", required=True)

    @api.model
    def _prepare_data(self, product):
        if self.increase_account_id:
            increase_account = self.increase_account_id
        else:
            increase_account = product.categ_id and \
                product.categ_id.\
                property_inventory_revaluation_increase_account_categ

        if self.decrease_account_id:
            decrease_account = self.decrease_account_id
        else:
            decrease_account = product.categ_id and \
                product.categ_id.\
                property_inventory_revaluation_decrease_account_categ

        return {
            'increase_account_id': increase_account.id,
            'decrease_account_id': decrease_account.id,
            'journal_id': self.journal_id.id,
            'remarks': self.remarks,
            'product_id': product.id,
            'amount': product.valuation_discrepancy
        }

    @api.multi
    def process(self):
        context = dict(self._context) or {}
        active_model = self.env.context['active_model']
        if active_model == 'product.product':
            products = self.env['product.product'].browse(
                context.get('active_ids', []))
        else:
            raise exceptions.Warning(
                _('Incorrect model.'))

        for product in products:
            if product.valuation != 'real_time':
                raise exceptions.Warning(
                    _('Product %s must have real time valuation') %
                    product.name)

        rec_ids = []
        for product in products:
            if not product.valuation_discrepancy:
                continue
            data = self._prepare_data(product)
            rec = self.env['stock.valuation.account.manual.adjustment'].create(
                data)
            rec.post()
            rec_ids.append(rec.id)

        return {
            'domain': [('id', 'in', rec_ids)],
            'name': _('Stock Valuation Account Manual Adjustments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.valuation.account.manual.adjustment',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
