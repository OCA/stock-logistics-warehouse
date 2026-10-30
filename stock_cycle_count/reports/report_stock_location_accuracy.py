# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class LocationAccuracyReport(models.AbstractModel):
    _name = "report.stock_cycle_count.stock_location_accuracy"
    _description = "Location Accuracy Report"

    @api.model
    def _get_inventory_domain(self, loc_id, exclude_sublocation=True):
        return [
            ("location_ids", "in", [loc_id]),
            ("exclude_sublocation", "=", exclude_sublocation),
            ("filter", "=", "none"),
            ("state", "=", "done"),
        ]

    @api.model
    def _get_location_data(self, locations):
        location_data = {}
        counts = self.env["stock.inventory"].search(
            [
                ("location_ids", "in", locations.ids),
                ("state", "=", "done"),
            ]
        )
        for loc in locations:
            location_data[loc] = counts.filtered(
                lambda count, loc=loc: loc in count.location_ids
            )
        return location_data

    def _get_report_values(self, docids, data=None):
        locations = self.env["stock.location"].browse(docids)
        location_data = self._get_location_data(locations)
        return {
            "doc_ids": locations.ids,
            "doc_model": "stock.location",
            "docs": locations,
            "location_data": location_data,
        }
