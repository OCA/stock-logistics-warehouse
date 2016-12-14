# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, fields, models, _
from openerp.addons import decimal_precision as dp
import operator
ops = {'=': operator.eq,
       '!=': operator.ne,
       '<=': operator.le,
       '>=': operator.ge,
       '>': operator.gt,
       '<': operator.lt}

UNIT = dp.get_precision('Account')


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def _get_internal_quant_domain(self):
        return [('product_id', '=', self.id),
                ('location_id.usage', '=', 'internal')]

    @api.model
    def get_inventory_value(self):
        domain = self._get_internal_quant_domain()
        quants = self.env['stock.quant'].read_group(
            domain, ['product_id', 'qty', 'cost'], ['product_id'])
        variant_qty = 0.0
        variant_value = 0.0
        for quant in quants:
            variant_qty += quant['qty']
            variant_value += quant['qty'] * quant['cost']
        if self.cost_method == 'real':
            return variant_value
        else:
            return variant_qty * self.standard_price

    @api.model
    def _get_account_move_line_inventory_domain(self):
        return [('product_id', '=', self.id),
                ('account_id', '=',
                 self.categ_id.property_stock_valuation_account_id.id),
                ('period_id.special', '=', False)]

    @api.model
    def get_accounting_value(self):
        domain = self._get_account_move_line_inventory_domain()
        amls = self.env['account.move.line'].read_group(
            domain, ['product_id', 'debit', 'credit'], ['product_id'])
        variant_value = 0.0
        for aml in amls:
            variant_value += aml['debit'] - aml['credit']
        return variant_value

    @api.multi
    def _compute_inventory_account_value(self):
        for rec in self:
            rec.inventory_value = rec.get_inventory_value()
            rec.accounting_value = self.get_accounting_value()
            rec.valuation_discrepancy = rec.inventory_value - \
                rec.accounting_value

    @api.multi
    def _compute_accounting_value(self):
        for rec in self:
            rec.accounting_value = self.get_accounting_value()

    inventory_value = fields.Float(string='Inventory Value',
                                   compute='_compute_inventory_account_value',
                                   digits=UNIT)
    accounting_value = fields.Float(string='Accounting Value',
                                    compute='_compute_inventory_account_value',
                                    digits=UNIT)
    valuation_discrepancy = fields.Float(
        string='Valuation discrepancy',
        compute='_compute_inventory_account_value',
        digits=UNIT)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def _compute_inventory_account_value(self):
        for rec in self:
            inv_value = 0.0
            acc_value = 0.0
            for variant in rec.product_variant_ids:
                inv_value += variant.get_inventory_value()
                acc_value += variant.get_accounting_value()
            rec.inventory_value = inv_value
            rec.accounting_value = acc_value
            rec.valuation_discrepancy = acc_value - inv_value

    @api.multi
    def _search_valuation_discrepancy(self, operator, value):
        """Search records with a valuation discrepancy"""
        all_records = self.search([('active', '=', True),
                                  ('valuation', '=', 'real_time')])
        if operator not in ops.keys():
            raise exceptions.Warning(
                _('Search operator %s not implemented for value %s')
                % (operator, value)
            )
        found_ids = [a.id for a in all_records
                     if ops[operator](a.valuation_discrepancy, value)]
        return [('id', 'in', found_ids)]

    inventory_value = fields.Float(string='Inventory Value',
                                   compute='_compute_inventory_account_value',
                                   digits=UNIT)
    accounting_value = fields.Float(string='Accounting Value',
                                    compute='_compute_inventory_account_value',
                                    digits=UNIT)
    valuation_discrepancy = fields.Float(
        string='Accounting - Inventory Value',
        compute='_compute_inventory_account_value',
        digits=UNIT,
        help="""Positive number means that the accounting valuation needs to
        decrease.""", search="_search_valuation_discrepancy")
