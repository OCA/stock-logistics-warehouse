# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import OrderedDict

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    warehouse_view_ids = fields.One2many(
        "stock.warehouse", "view_location_id", readonly=True
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", compute="_compute_warehouse_id", store=True
    )

    @api.depends("warehouse_view_ids", "parent_path")
    def _compute_warehouse_id(self):
        self.invalidate_cache(["parent_path", "warehouse_view_ids"])
        warehouses = (
            self.env["stock.warehouse"].with_context(active_test=False).search([])
        )
        view_by_wh = OrderedDict((wh.view_location_id.id, wh.id) for wh in warehouses)
        for loc in self:
            if not loc.parent_path:
                continue
            path = [int(loc_id) for loc_id in loc.parent_path.split("/")[:-1]]
            for view_location_id in view_by_wh:
                if len(path) > 1 and view_location_id == path[1]:
                    loc.warehouse_id = view_by_wh[view_location_id]
                    break
