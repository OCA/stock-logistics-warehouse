# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class inventory_add_multiple(models.TransientModel):
    _name = 'inventory.add_multiple'
    _description = 'Inventory add multiple'

    products_ids = fields.Many2many(
        'product.product',
        string='Products')

    @api.one
    def add_multiple(self):
        active_id = self._context['active_id']
        inventory = self.env['stock.inventory'].browse(active_id)
        for product_id in self.products_ids:
            product = self.env['stock.inventory.line'].onchange_createline(
                inventory.location_id.id,
                product_id.id,
                product_id.uom_id.id
            )
            val = {
                'inventory_id': active_id,
                'product_uom_id': product_id.uom_id.id,
                'location_id': inventory.location_id.id,
                'product_id': product_id.id or False,
                'product_qty': product['value'].get('product_qty'),
                'theorical_qty': product['value'].get('theoretical_qty')
            }
            self.env['stock.inventory.line'].create(val)
