# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocationTrayType(models.Model):
    _inherit = "stock.location.tray.type"

    storage_category_id = fields.Many2one(
        comodel_name="stock.storage.category",
        string="Storage Category",
    )

    def write(self, values):
        res = super().write(values)
        if values.get("storage_category_id"):
            self._sync_storage_category_id()
        return res

    def _sync_storage_category_id(self):
        for tray_type in self:
            tray_type.location_ids.with_context(_sync_tray_type=True).write(
                {
                    "storage_category_id": tray_type.storage_category_id.id,
                }
            )
