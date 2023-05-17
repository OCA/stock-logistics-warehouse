# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    @api.depends("production_ids")
    def _compute_purchase_ids(self):
        super()._compute_purchase_ids()
        for item in self.filtered(lambda x: x.production_ids):
            moves = item.production_ids.procurement_group_id.stock_move_ids
            production_purchases = (
                moves.created_purchase_line_id.order_id
                | moves.move_orig_ids.purchase_line_id.order_id
            )
            item.purchase_ids += production_purchases
            item.purchase_count = len(item.purchase_ids)
