# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("product_id", "product_uom_id")
    def _onchange_product_id(self):
        origin_product_uom = self.product_uom_id
        res = super()._onchange_product_id()
        # We impose the purchase uom if the operation type has the use_purchase_uom enabled
        # and we are creating the line and the stock_move_line is not linked to a stock_move.
        if (
            self.picking_type_id
            and self.picking_type_id.use_purchase_uom
            and not self.move_id
            and not origin_product_uom
            and self.product_id
        ):
            self.product_uom_id = self.product_id.uom_po_id.id
        return res
