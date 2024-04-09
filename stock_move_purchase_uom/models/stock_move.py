# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange("product_id", "picking_type_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id:
            if self.picking_type_id and self.picking_type_id.use_purchase_uom:
                self.product_uom = self.product_id.with_context(
                    lang=self._get_lang()
                ).uom_po_id.id
        return res
