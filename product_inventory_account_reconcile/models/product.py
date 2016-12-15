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

    @api.multi
    def _compute_inventory_account_value(self):
        self.env.cr.execute("""
            SELECT aml.product_id, sum(debit) - sum(credit) as valuation
            FROM account_move_line as aml
            INNER JOIN account_period as ap
            ON ap.id = aml.period_id
            INNER JOIN product_product as pr
            ON pr.id = aml.product_id
            INNER JOIN product_template as pt
            ON pt.id = pr.product_tmpl_id
            INNER JOIN ir_property as ip
            on (ip.res_id = 'product.category,' || pt.categ_id
            AND ip.name = 'property_stock_valuation_account_id'
            AND 'account.account,' || aml.account_id = ip.value_reference)
            GROUP BY aml.product_id
        """)
        accounting_val = {}
        for product_id, valuation in self.env.cr.fetchall():
            accounting_val[product_id] = valuation
        for rec in self:
            rec.inventory_value = rec.get_inventory_value()
            if rec.id in accounting_val.keys():
                rec.accounting_value = accounting_val[rec.id]
            else:
                rec.accounting_value = 0.0
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
        self.env.cr.execute("""
            SELECT pt.id, sum(debit) - sum(credit) as valuation
            FROM account_move_line as aml
            INNER JOIN account_period as ap
            ON ap.id = aml.period_id
            INNER JOIN product_product as pr
            ON pr.id = aml.product_id
            INNER JOIN product_template as pt
            ON pt.id = pr.product_tmpl_id
            INNER JOIN ir_property as ip
            on (ip.res_id = 'product.category,' || pt.categ_id
            AND ip.name = 'property_stock_valuation_account_id'
            AND 'account.account,' || aml.account_id = ip.value_reference)
            GROUP BY pt.id
        """)
        accounting_val = {}
        for template_id, valuation in self.env.cr.fetchall():
            accounting_val[template_id] = valuation
        for rec in self:
            inv_value = 0.0
            if rec.id in accounting_val.keys():
                acc_value = accounting_val[rec.id]
            else:
                acc_value = 0.0
            for variant in rec.product_variant_ids:
                inv_value += variant.get_inventory_value()
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

    inventory_value = fields.Float(
        string='Inventory Value', compute='_compute_inventory_account_value',
        digits=UNIT, groups="product_inventory_account_reconcile"
                            ".group_product_inventory_account_reconcile")
    accounting_value = fields.Float(
        string='Accounting Value', compute='_compute_inventory_account_value',
        digits=UNIT, groups="product_inventory_account_reconcile"
                            ".group_product_inventory_account_reconcile")
    valuation_discrepancy = fields.Float(
        string='Valuation discrepancy',
        compute='_compute_inventory_account_value',
        digits=UNIT,
        help="""Positive number means that the accounting valuation needs to
        decrease.""", search="_search_valuation_discrepancy",
        groups="product_inventory_account_reconcile"
               ".group_product_inventory_account_reconcile")
