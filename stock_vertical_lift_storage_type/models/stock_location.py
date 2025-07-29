# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("_sync_tray_type"):
            for vals in vals_list:
                if vals.get("tray_type_id") and vals.get("storage_category_id"):
                    raise exceptions.UserError(
                        self.env._(
                            "Error creating '%(name)s': Location storage"
                            " category must be set on the tray type",
                            name=vals.get("name"),
                        )
                    )

        records = super().create(vals_list)
        records._sync_tray_type_storage_category()
        return records

    def write(self, values):
        if not self.env.context.get("_sync_tray_type"):
            if values.get("storage_category_id"):
                if values.get("tray_type_id"):
                    has_tray_type = self
                else:
                    has_tray_type = self.filtered("tray_type_id")
                if has_tray_type:
                    raise exceptions.UserError(
                        self.env._(
                            "Error updating '%(name)s': Location storage"
                            " category must be set on the tray type",
                            name=", ".join(has_tray_type.mapped("name")),
                        )
                    )
        res = super().write(values)
        if values.get("tray_type_id"):
            self._sync_tray_type_storage_category()
        return res

    def _sync_tray_type_storage_category(self):
        for location in self.with_context(_sync_tray_type=True):
            if not location.tray_type_id:
                continue
            location.storage_category_id = location.tray_type_id.storage_category_id
