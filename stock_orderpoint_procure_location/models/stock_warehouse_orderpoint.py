# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    procure_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Procurement Location",
        domain="[('usage', '=', 'internal')]",
    )

    def _prepare_procurement_values(self, date=False, group=False):
        """Set the procure location"""
        res = super(Orderpoint, self)._prepare_procurement_values(date, group)
        if self.procure_location_id:
            res["procure_location_id"] = self.procure_location_id
        return res

    def _quantity_in_progress(self):
        res = super()._quantity_in_progress()
        not_count_states = ["done", "cancel"]
        for orderpoint in self:
            for sm in (
                self.env["purchase.order.line"]
                .search(
                    [
                        ("state", "=", "purchase"),
                        ("product_id", "=", orderpoint.product_id.id),
                    ]
                )
                .mapped("move_ids")
                .filtered(
                    lambda m: m.location_dest_id == orderpoint.procure_location_id
                    and m.state not in not_count_states
                )
            ):
                res[orderpoint.id] += sm.product_uom._compute_quantity(
                    sm.product_qty, sm.product_uom, round=False
                )
        return res
