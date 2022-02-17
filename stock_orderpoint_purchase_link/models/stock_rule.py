# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        vals = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        if "orderpoint_id" in values and values["orderpoint_id"].id:
            vals["orderpoint_ids"] = [(4, values["orderpoint_id"].id)]
        # If the procurement was run by a stock move.
        elif "orderpoint_ids" in values:
            vals["orderpoint_ids"] = [(4, o.id) for o in values["orderpoint_ids"]]
        return vals
