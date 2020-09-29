# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("_sync_tray_type"):
            for vals in vals_list:
                if vals.get("tray_type_id") and vals.get("location_storage_type_ids"):
                    raise exceptions.UserError(
                        _(
                            "Error creating '{}': Location storage"
                            " type must be set on the tray type"
                        ).format(vals.get("name"))
                    )

        records = super().create(vals_list)
        records._sync_tray_type_storage_types()
        return records

    def write(self, values):
        if not self.env.context.get("_sync_tray_type"):
            if values.get("location_storage_type_ids"):
                if values.get("tray_type_id"):
                    has_tray_type = self
                else:
                    has_tray_type = self.filtered("tray_type_id")
                if has_tray_type:
                    raise exceptions.UserError(
                        _(
                            "Error updating {}: Location storage"
                            " type must be set on the tray type"
                        ).format(", ".join(has_tray_type.mapped("name")))
                    )
        res = super().write(values)
        if values.get("tray_type_id"):
            self._sync_tray_type_storage_types()
        return res

    def _sync_tray_type_storage_types(self):
        for location in self.with_context(_sync_tray_type=True):
            if not location.tray_type_id:
                continue
            storage_types = location.tray_type_id.location_storage_type_ids
            location.write({"location_storage_type_ids": [(6, 0, storage_types.ids)]})
