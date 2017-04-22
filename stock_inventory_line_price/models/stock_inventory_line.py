# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    theoretical_std_price = fields.Float(
        string='Theoretical Cost Price',
        digits=dp.get_precision('Product Price'),
        readonly=True,
    )
    standard_price = fields.Float(
        string='Cost Price',
        digits=dp.get_precision('Product Price'),
    )

    @api.model
    def _resolve_inventory_line(self, inventory_line):

        super_method = super(StockInventoryLine, self)._resolve_inventory_line
        theoretical_price = inventory_line.theoretical_std_price
        standard_price = inventory_line.standard_price

        if theoretical_price == standard_price:
            return super_method(inventory_line)

        inventory_line.product_id.standard_price = standard_price
        move_id = super_method(inventory_line)

        if move_id:
            move = self.env['stock.move'].browse(move_id)
            move.price_unit = standard_price

        return move_id
