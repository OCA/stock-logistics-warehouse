# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


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

    @api.multi
    def _get_move_values(self, qty, location_id, location_dest_id):
        vals = super(StockInventoryLine, self)._get_move_values(
            qty, location_id, location_dest_id,
        )
        vals.update({
            'price_unit': self.standard_price,
        })
        return vals

    @api.multi
    def _generate_moves(self):

        moves = self.env['stock.move']

        for inventory_line in self:

            super_method = super(
                StockInventoryLine, inventory_line,
            )
            super_method = super_method._generate_moves

            theoretical_price = inventory_line.theoretical_std_price
            standard_price = inventory_line.standard_price

            if theoretical_price == standard_price:
                moves += super_method()
                continue

            inventory_line.product_id.standard_price = standard_price
            moves += super_method()

        return moves
