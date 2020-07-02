# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocationTrayType(models.Model):
    _inherit = "stock.location.tray.type"

    location_storage_type_ids = fields.Many2many(
        comodel_name="stock.location.storage.type",
        help="Location storage types applied on the location using " "this tray type.",
    )

    def write(self, values):
        res = super().write(values)
        if values.get("location_storage_type_ids"):
            self._sync_location_storage_type_ids()
        return res

    def _sync_location_storage_type_ids(self):
        for tray_type in self:
            tray_type.location_ids.with_context(_sync_tray_type=True).write(
                {
                    "location_storage_type_ids": [
                        (6, 0, tray_type.location_storage_type_ids.ids)
                    ]
                }
            )
