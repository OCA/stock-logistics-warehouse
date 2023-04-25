# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class StockLocation(models.Model):
    _inherit = "stock.location"

    location_orderpoint_ids = fields.One2many(
        comodel_name="stock.location.orderpoint",
        inverse_name="location_id",
        string="Location Orderpoints",
        help="Location Orderpoints. Rules that allows this location to be replenished.",
    )
    location_orderpoint_count = fields.Integer(
        compute="_compute_location_orderpoint_count",
    )

    def _compute_location_orderpoint_count(self):
        groups = self.env["stock.location.orderpoint"].read_group(
            [("location_id", "in", self.ids)], ["location_id"], ["location_id"]
        )
        result = {
            data["location_id"][0]: (data["location_id_count"]) for data in groups
        }
        for location in self:
            location.location_orderpoint_count = result.get(location.id, 0)

    def action_open_location_orderpoints(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_location_orderpoint.action_stock_location_orderpoint"
        )
        action["domain"] = [("location_id", "in", self.ids)]
        if len(self.ids) == 1:
            if "context" in action:
                context = safe_eval(action["context"])
                context.update({"default_location_id": self.id})
                action["context"] = str(context)
            else:
                action["context"] = str({"default_location_id": self.id})
        return action
