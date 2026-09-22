# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super()._action_done()

        for line in self:
            lot = line.lot_id
            if not lot or lot.product_tracking != "serial":
                continue

            src_usage = line.location_id.usage
            dest_usage = line.location_dest_id.usage

            if dest_usage == "customer":
                lot._update_customer_warranty_on_delivery(line)
            if src_usage == "customer":
                lot._reset_customer_warranty_on_return(line)
            if src_usage == "supplier":
                lot._update_vendor_warranty_on_receipt(line)
            if dest_usage == "supplier":
                lot._reset_vendor_warranty_on_return(line)
        return res
