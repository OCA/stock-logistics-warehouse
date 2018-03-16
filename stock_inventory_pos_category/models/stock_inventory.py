# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    pos_categ_ids = fields.Many2many(
        'pos.category', string='Point of Sale Categories',
        readonly=True, states={'draft': [('readonly', False)]},
        help="Specify one or several point of sale categories to focus "
        "your inventory on specific point of sale categories")

    @api.model
    def _selection_filter(self):
        res_filter = super(StockInventory, self)._selection_filter()
        res_filter.append(('pos_categories', _('Point of Sale Categories')))
        return res_filter

    @api.onchange('filter')
    def onchange_filter(self):
        super(StockInventory, self).onchange_filter()
        if self.filter != 'pos_categories':
            self.pos_categ_ids = False

    @api.constrains('filter', 'pos_categ_ids')
    def _check_filter_pos_categories(self):
        for inv in self:
            if inv.filter != 'pos_categories' and inv.pos_categ_ids:
                raise ValidationError(_(
                    'The selected inventory options are not coherent.'))

    @api.multi
    def _get_inventory_lines_values(self):
        vals = super(StockInventory, self)._get_inventory_lines_values()
        if self.pos_categ_ids:
            locations = self.env['stock.location'].search([
                ('id', 'child_of', [self.location_id.id])])
            vals = []
            Product = self.env['product.product']
            quant_products = self.env['product.product']
            products_to_filter = self.env['product.product']
            pos_categ_products = Product.search([
                ('pos_categ_id', 'child_of', self.pos_categ_ids.ids)])
            products_to_filter |= pos_categ_products

            self.env.cr.execute("""
                SELECT product_id, sum(qty) as product_qty, location_id,
                lot_id as prod_lot_id, package_id, owner_id as partner_id
                FROM stock_quant
                WHERE location_id in %s AND company_id = %s AND
                product_id = ANY (%s)
                GROUP BY product_id, location_id, lot_id,
                package_id, partner_id
                """, (tuple(locations.ids), self.company_id.id,
                      pos_categ_products.ids))
            # copy-pasted from odoo/addons/stock/models/stock_inventory.py
            # So it is copyright Odoo S.A.
            for product_data in self.env.cr.dictfetchall():
                # replace the None the dictionary by False,
                # because falsy values are tested later on
                for void_field in [
                        item[0] for item in product_data.items()
                        if item[1] is None]:
                    product_data[void_field] = False
                product_data['theoretical_qty'] = product_data['product_qty']
                if product_data['product_id']:
                    product_data['product_uom_id'] = Product.browse(
                        product_data['product_id']).uom_id.id
                    quant_products |= Product.browse(
                        product_data['product_id'])
                vals.append(product_data)
            if self.exhausted:
                exhausted_vals = self._get_exhausted_inventory_line(
                    products_to_filter, quant_products)
                vals.extend(exhausted_vals)
        return vals
