# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for warehouse in res:
            warehouse_locations = self.env["stock.location"].search(
                [("id", "child_of", warehouse.view_location_id.id)]
            )
            self.env["stock.reserve.area"].sudo().create(
                {
                    "name": warehouse.name,
                    "location_ids": [(6, 0, warehouse_locations.ids)],
                }
            )
        return res
