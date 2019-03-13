# Copyright 2019 Jarsa Sistemas, www.vauxoo.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _adjust_procure_method(self):
        for move in self.move_raw_ids:
            qty_available = move.product_id.qty_available
            move_qty = move.product_uom_qty
            if qty_available == 0.0:
                move.procure_method = 'make_to_order'
            elif move_qty > qty_available and qty_available != 0.0:
                move.copy({
                    'product_uom_qty': move_qty - qty_available,
                    'procure_method': 'make_to_order'})
                move.product_uom_qty = qty_available
