# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_utils


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    virtual_location_id = fields.Many2one(
        comodel_name='stock.location',
        domain=[('usage', 'like', 'inventory')],
    )

    def _generate_moves(self):
        moves = move_obj = self.env['stock.move']
        unusual_lines = self.filtered(
            lambda l: l.virtual_location_id and
            l.virtual_location_id != l.product_id.property_stock_inventory)
        usual_lines = self - unusual_lines
        for line in unusual_lines:
            if float_utils.float_compare(
                    line.theoretical_qty, line.product_qty,
                    precision_rounding=line.product_id.uom_id.rounding) == 0:
                continue
            diff = line.theoretical_qty - line.product_qty
            if float_utils.float_compare(  # found more than expected
                    diff, 0.0,
                    precision_rounding=line.product_uom_id.rounding) < 0:
                vals = line._get_move_values(
                    abs(diff),
                    line.virtual_location_id.id,
                    line.location_id.id, False)
            else:
                vals = line._get_move_values(
                    abs(diff),
                    line.location_id.id,
                    line.virtual_location_id.id, True)
            moves |= move_obj.create(vals)
        moves |= super(StockInventoryLine, usual_lines)._generate_moves()
        return moves
