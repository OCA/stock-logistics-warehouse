# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    exclude_sublocation = fields.Boolean(string='Exclude Sublocations',
                                         default=False)

    @api.model
    def _get_inventory_lines(self, inventory):
        if inventory.exclude_sublocation:
            product_obj = self.env['product.product']
            domain = ' location_id = %s'
            args = (tuple(inventory.location_id.ids))
            if inventory.partner_id:
                domain += ' and owner_id = %s'
                args += (inventory.partner_id.id,)
            if inventory.lot_id:
                domain += ' and lot_id = %s'
                args += (inventory.lot_id.id,)
            if inventory.product_id:
                domain += ' and product_id = %s'
                args += (inventory.product_id.id,)
            if inventory.package_id:
                domain += ' and package_id = %s'
                args += (inventory.package_id.id,)

            self.env.cr.execute('''
               SELECT product_id, sum(qty) as product_qty, location_id, lot_id
               as prod_lot_id, package_id, owner_id as partner_id
               FROM stock_quant WHERE''' + domain + '''
               GROUP BY product_id, location_id, lot_id, package_id, partner_id
            ''', args)
            vals = []
            for product_line in self.env.cr.dictfetchall():
                for key, value in product_line.items():
                    if not value:
                        product_line[key] = False
                product_line['inventory_id'] = inventory.id
                product_line['theoretical_qty'] = product_line['product_qty']
                if product_line['product_id']:
                    product = product_obj.browse(product_line['product_id'])
                    product_line['product_uom_id'] = product.uom_id.id
                vals.append(product_line)
            return vals
        else:
            return super(StockInventory, self)._get_inventory_lines(inventory)
