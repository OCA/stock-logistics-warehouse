# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    last_inventory_date = fields.Datetime(
        "Last Inventory Date",
        compute="_compute_last_inventory_date",
        help="Indicates the last inventory date for the location, "
        "including inventory done on parents location.",
    )

    def _compute_last_inventory_date(self):
        for location in self:
            location_ids = [
                int(location_id)
                for location_id in location.parent_path.rstrip("/").split("/")
            ]
            last_inventory = self.env["stock.inventory"].search(
                [("location_ids", "in", location_ids), ("state", "=", "done")],
                order="date desc",
                limit=1,
            )
            location.last_inventory_date = last_inventory.date
