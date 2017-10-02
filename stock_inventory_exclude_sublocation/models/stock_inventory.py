# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Inventory(models.Model):
    _inherit = 'stock.inventory'

    exclude_sublocation = fields.Boolean(
        string='Exclude Sublocations', default=False,
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.multi
    def _get_inventory_lines_values(self):
        if self.exclude_sublocation:
            domain = ' location_id = %s'
            args = (tuple(self.location_id.ids),)

            vals = []
            product_obj = self.env['product.product']
            # Empty recordset of products available in stock_quants
            quant_products = self.env['product.product']
            # Empty recordset of products to filter
            products_to_filter = self.env['product.product']

            if self.company_id.id:
                domain += ' and company_id = %s'
                args += (self.company_id.id,)
            if self.partner_id:
                domain += ' and owner_id = %s'
                args += (self.partner_id.id,)
            if self.lot_id:
                domain += ' and lot_id = %s'
                args += (self.lot_id.id,)
            if self.product_id:
                domain += ' and product_id = %s'
                args += (self.product_id.id,)
                products_to_filter |= self.product_id
            if self.package_id:
                domain += ' and package_id = %s'
                args += (self.package_id.id,)
            if self.category_id:
                categ_products = product_obj.search(
                    [('categ_id', '=', self.category_id.id)])
                domain += ' AND product_id = ANY (%s)'
                args += (categ_products.ids,)
                products_to_filter |= categ_products

            self.env.cr.execute("""
                SELECT product_id, sum(qty) as product_qty, location_id, lot_id
                    as prod_lot_id, package_id, owner_id as partner_id
                FROM stock_quant
                WHERE %s
                GROUP BY product_id, location_id, lot_id, package_id,
                    partner_id """ % domain, args)

            for product_data in self.env.cr.dictfetchall():
                for void_field in [item[0] for item in product_data.items() if
                                   item[1] is None]:
                    product_data[void_field] = False
                product_data['theoretical_qty'] = product_data['product_qty']
                if product_data['product_id']:
                    product_data['product_uom_id'] = product_obj.browse(
                        product_data['product_id']).uom_id.id
                    quant_products |= product_obj.browse(
                        product_data['product_id'])
                vals.append(product_data)
            if self.exhausted:
                exhausted_vals = self._get_exhausted_inventory_line(
                    products_to_filter, quant_products)
                vals.extend(exhausted_vals)
            return vals
        else:
            return super(Inventory, self)._get_inventory_lines_values()
