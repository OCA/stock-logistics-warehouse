# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
import operator

ops = {'=': operator.eq,
       '!=': operator.ne,
       '<=': operator.le,
       '>=': operator.ge,
       '>': operator.gt,
       '<': operator.lt}

UNIT = dp.get_precision('Account')


class ProductProduct(models.Model):
    _inherit = "product.product"

    inventory_value = fields.Float(
        string="Inventory Value", compute="_compute_inventory_account_value",
        search="_search_inventory_value", digits=UNIT,
        groups="stock_valuation_account_manual_adjustment."
               "group_stock_valuation_account_manual_adjustment",
    )
    accounting_value = fields.Float(
        string="Accounting Value", compute="_compute_inventory_account_value",
        search="_search_accounting_value", digits=UNIT,
        groups="stock_valuation_account_manual_adjustment."
               "group_stock_valuation_account_manual_adjustment",
    )
    valuation_discrepancy = fields.Float(
        string="Valuation discrepancy",
        compute="_compute_inventory_account_value",
        search="_search_valuation_discrepancy", digits=UNIT,
        groups="stock_valuation_account_manual_adjustment."
               "group_stock_valuation_account_manual_adjustment",
    )

    @api.multi
    def _compute_inventory_account_value(self):
        accounting_val = self._get_accounting_valuation_by_product()
        inventory_val = self._get_inventory_valuation_by_product()
        for product in self:
            inventory_v = inventory_val.get(product.id, 0.0)
            accounting_v = accounting_val.get(product.id, 0.0)
            product.accounting_value = accounting_v
            product.inventory_value = inventory_v
            product.valuation_discrepancy = inventory_v - accounting_v

    @api.model
    def _get_accounting_valuation_by_product(self):
        accounting_val = {}
        # pylint: disable=E8103
        query = """
            SELECT aml.product_id, sum(debit) - sum(credit)
            as valuation
            FROM account_move_line as aml
            INNER JOIN product_product as pr
            ON pr.id = aml.product_id
            INNER JOIN product_template as pt
            ON pt.id = pr.product_tmpl_id
            INNER JOIN ir_property as ip
            on (ip.res_id IS NULL
            AND ip.name =
            'property_stock_valuation_account_id'
            AND 'account.account,' || aml.account_id =
            ip.value_reference AND ip.company_id = %s)
            AND ip.id NOT IN (
                SELECT id
                FROM ir_property
                WHERE res_id = 'product.category,' ||
                pt.categ_id
                AND name =
                'property_stock_valuation_account_id'
                AND ip.company_id = %s
            )
            AND aml.company_id = %s
            GROUP BY aml.product_id
        """
        params = (self.env.user.company_id.id,
                  self.env.user.company_id.id, self.env.user.company_id.id)
        query = query % params
        self.env.cr.execute(query, params=params)

        for product_id, valuation in self.env.cr.fetchall():
            accounting_val[product_id] = valuation
        return accounting_val

    @api.model
    def _get_internal_quant_domain_search(self):
        return [('product_id.type', '=', 'product'),
                ('location_id.usage', '=', 'internal')]

    @api.model
    def _get_inventory_valuation_by_product(self):
        inventory_val = {}
        # pylint: disable=E8103
        query = """
            WITH Q1 AS (
                SELECT pt.id, ip.value_text as cost_method
                FROM product_template as pt
                INNER JOIN ir_property as ip
                ON (ip.res_id = 'product.category,' || pt.categ_id)
                INNER JOIN ir_model_fields imf
                ON imf.id = ip.fields_id
                AND ip.company_id = %s
                AND imf.name = 'property_cost_method'),
            Q2 AS (
                SELECT pt.id, ip.value_text as cost_method
                FROM product_template as pt
                INNER JOIN ir_property as ip
                ON (ip.res_id IS NULL)
                INNER JOIN ir_model_fields imf
                ON imf.id = ip.fields_id
                AND imf.name = 'property_cost_method'
                WHERE pt.id NOT IN (SELECT id FROM Q1) AND ip.company_id = %s),
            Q3 AS (
                SELECT * FROM Q1
                UNION ALL
                SELECT * FROM Q2),
            Q4 AS (
                SELECT pr.id, sum(sq.qty*sq.cost) as valuation
                FROM stock_quant as sq
                INNER JOIN product_product as pr
                ON pr.id = sq.product_id
                INNER JOIN stock_location as sl
                ON sl.id = sq.location_id
                INNER JOIN Q3
                ON Q3.id = pr.product_tmpl_id
                WHERE Q3.cost_method = 'real'
                AND sl.usage = 'internal'
                AND sq.company_id = %s
                GROUP BY pr.id),
            Q5 AS (
                SELECT pr.id, sum(sq.qty*ip.value_float) as valuation
                FROM stock_quant as sq
                INNER JOIN product_product as pr
                ON pr.id = sq.product_id
                INNER JOIN stock_location as sl
                ON sl.id = sq.location_id
                INNER JOIN Q3
                ON (Q3.id = pr.product_tmpl_id
                AND Q3.cost_method in ('standard', 'average'))
                INNER JOIN ir_property as ip
                ON (ip.res_id = 'product.product,' || pr.id)
                INNER JOIN ir_model_fields imf
                ON (imf.id = ip.fields_id
                AND imf.name = 'standard_price')
                WHERE sl.usage = 'internal'
                AND sq.company_id = %s
                GROUP BY pr.id),
            Q6 AS (
                SELECT * FROM Q4 UNION ALL SELECT * FROM Q5),
            Q7 AS (
                SELECT * FROM Q6 UNION ALL SELECT pr.id, 0.0
                FROM product_product as pr
                WHERE pr.id NOT IN (select id from Q6))
            SELECT *
            FROM Q7
        """
        params = (self.env.user.company_id.id, self.env.user.company_id.id,
                  self.env.user.company_id.id, self.env.user.company_id.id)

        self.env.cr.execute(query, params=params)
        for product_id, valuation in self.env.cr.fetchall():
            inventory_val[product_id] = valuation
        return inventory_val

    @api.multi
    def _search_accounting_value(self, operator, value):
        if operator not in ops.keys():
            raise UserError(
                _('Search operator %s not implemented for value %s')
                % (operator, value)
            )
        accounting_val = self._get_accounting_valuation_by_product()
        products = self.search([
            ('active', '=', True),
            ('categ_id.property_valuation', '=', 'real_time')])
        found_ids = []
        for product in products:
            accounting_v = accounting_val.get(product.id, 0.0)
            if ops[operator](accounting_v, value):
                found_ids.append(product.id)
        return [('id', 'in', found_ids)]

    @api.multi
    def _search_inventory_value(self, operator, value):
        if operator not in ops.keys():
            raise UserError(
                _('Search operator %s not implemented for value %s')
                % (operator, value)
            )
        inventory_val = self._get_inventory_valuation_by_product()
        products = self.search([
            ('active', '=', True),
            ('categ_id.property_valuation', '=', 'real_time')])
        found_ids = []
        for product in products:
            inventory_v = inventory_val.get(product.id, 0.0)
            if ops[operator](inventory_v, value):
                found_ids.append(product.id)
        return [('id', 'in', found_ids)]

    @api.multi
    def _search_valuation_discrepancy(self, operator, value):
        if operator not in ops.keys():
            raise UserError(
                _('Search operator %s not implemented for value %s')
                % (operator, value)
            )
        accounting_val = self._get_accounting_valuation_by_product()
        inventory_val = self._get_inventory_valuation_by_product()
        products = self.search([
            ('active', '=', True),
            ('categ_id.property_valuation', '=', 'real_time')])
        found_ids = []
        for product in products:
            inventory_v = inventory_val.get(product.id, 0.0)
            accounting_v = accounting_val.get(product.id, 0.0)
            valuation_discrepancy = inventory_v - accounting_v
            if ops[operator](valuation_discrepancy, value):
                found_ids.append(product.id)
        return [('id', 'in', found_ids)]
