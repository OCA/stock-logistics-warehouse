# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        # Computes the second quantity for the return picking
        new_picking, pick_type_id = super()._create_returns()
        picking = self.env["stock.picking"].browse(new_picking)
        for move in picking.move_ids:
            if move.product_uom_qty and move.secondary_uom_id:
                factor = move.secondary_uom_id.factor or 1.0
                move.secondary_uom_qty = move.product_uom_qty / factor
        return new_picking, pick_type_id
