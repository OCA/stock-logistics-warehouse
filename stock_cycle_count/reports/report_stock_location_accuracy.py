# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class LocationAccuracyReport(models.AbstractModel):
    _name = "report.stock_location_accuracy"
    _description = "Location Accuracy Report"

    @api.model
    def _get_inventory_domain(self, loc_id, exclude_sublocation=True):
        return [
            ("location_id", "=", loc_id),
            ("exclude_sublocation", "=", exclude_sublocation),
            ("filter", "=", "none"),
            ("state", "=", "done"),
        ]

    @api.model
    def _get_location_data(self, locations):
        data = dict()
        inventory_obj = self.env["stock.inventory"]
        for loc in locations:
            counts = inventory_obj.search(self._get_inventory_domain(loc.id))
            data[loc] = counts
        return data

    def render_html(self, data=None):
        report_obj = self.env["report"]
        locs = self.env["stock.location"].browse(self._ids)
        data = self._get_location_data(locs)
        docargs = {"doc_ids": locs._ids, "docs": locs, "data": data}
        return report_obj.render("stock_cycle_count.stock_location_accuracy", docargs)
