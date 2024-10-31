# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    children_location_ids = fields.Many2many(
        comodel_name="stock.location",
        compute="_compute_children_location_ids",
        help="All the children of this stock location (without this location).",
    )

    @api.depends("parent_path", "location_id")
    def _compute_children_location_ids(self):
        """
        Compute the children locations of the current recordset.
        Retrieve only ids and corresponding parent_path in order to get result with
        great performances.
        Don't include the current record.
        """
        locations = self.search_read(
            [("id", "child_of", self.ids), ("id", "not in", self.ids)],
            fields=["parent_path"],
        )
        for location in self:
            location.children_location_ids = [
                loc.get("id")
                for loc in locations
                if location.parent_path in loc.get("parent_path")
                and loc.get("id") != location.id
            ]

    def action_show_children_locations(self):
        """
        Display all children locations of the current one
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_location_form"
        )
        action.update(
            {
                "domain": [("id", "in", self.children_location_ids.ids)],
            }
        )
        return action
