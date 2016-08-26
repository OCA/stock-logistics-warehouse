# -*- coding: utf-8 -*-
# (c) 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    standard_price = fields.Float('Cost Price',
                                  digits=dp.get_precision('Product Price'))

    @api.model
    def _resolve_inventory_line(self, inventory_line):
        inventory_line.product_id.standard_price = \
            inventory_line.standard_price
        move_id = super(StockInventoryLine,
                        self)._resolve_inventory_line(inventory_line)
        if move_id:
            move = self.env['stock.move'].browse(move_id)
            move.price_unit = inventory_line.standard_price
        return move_id


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = super(StockInventory, self)._get_inventory_lines(inventory)
        for line in vals:
            product = self.env['product.product'].browse(line['product_id'])
            line.update({'standard_price': product.standard_price})
        return vals
