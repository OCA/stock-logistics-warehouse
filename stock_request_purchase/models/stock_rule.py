# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com).
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
        if "stock_request_id" in values:
            vals["stock_request_ids"] = [(4, values["stock_request_id"])]
        return vals
