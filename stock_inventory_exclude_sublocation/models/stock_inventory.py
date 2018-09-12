# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Inventory(models.Model):
    _inherit = 'stock.inventory'

    exclude_sublocation = fields.Boolean(
        string='Exclude Sublocations', default=False,
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)]})

    def _get_inventory_lines_values(self):
        """This method is a copy of standard one but considering only the
        current location.
        WARNING: In case of excluding sublocations standard method
        is overridden by this one."""
        if not self.exclude_sublocation:
            # Early return if exclude_sublocation is not set
            return super()._get_inventory_lines_values()

        # STAR OF MODIFIED CODE:
        domain = ' location_id in %s'
        args = (tuple(self.location_id.ids),)
        # END OF MODIFIED CODE.

        vals = []
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']
        # Empty recordset of products to filter
        products_to_filter = self.env['product.product']

        # case 0: Filter on company
        if self.company_id:
            domain += ' AND company_id = %s'
            args += (self.company_id.id,)

        # case 1: Filter on One owner only or One product for a specific owner
        if self.partner_id:
            domain += ' AND owner_id = %s'
            args += (self.partner_id.id,)
        # case 2: Filter on One Lot/Serial Number
        if self.lot_id:
            domain += ' AND lot_id = %s'
            args += (self.lot_id.id,)
        # case 3: Filter on One product
        if self.product_id:
            domain += ' AND product_id = %s'
            args += (self.product_id.id,)
            products_to_filter |= self.product_id
        # case 4: Filter on A Pack
        if self.package_id:
            domain += ' AND package_id = %s'
            args += (self.package_id.id,)
        # case 5: Filter on One product category + Exahausted Products
        if self.category_id:
            categ_products = Product.search(
                [('categ_id', '=', self.category_id.id)])
            domain += ' AND product_id = ANY (%s)'
            args += (categ_products.ids,)
            products_to_filter |= categ_products

        self.env.cr.execute("""
            SELECT product_id, sum(quantity) as product_qty,
                location_id, lot_id as prod_lot_id, package_id,
                owner_id as partner_id
            FROM stock_quant
            WHERE %s
            GROUP BY product_id, location_id, lot_id,
                package_id, partner_id """ % domain, args)

        for product_data in self.env.cr.dictfetchall():
            for void_field in [item[0] for item in product_data.items() if
                               item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(
                    product_data['product_id']).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)
        if self.exhausted:
            exhausted_vals = self._get_exhausted_inventory_line(
                products_to_filter, quant_products)
            vals.extend(exhausted_vals)
        return vals
