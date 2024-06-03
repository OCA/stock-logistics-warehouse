# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_location_fields(self):
        location_fields = []

        for field, definition in self.fields_get().items():
            if definition.get("relation") == "stock.location":
                location_fields.append(field)

        return location_fields

    def _check_locations_linked_to_warehouse(self):
        location_ids = self.env["stock.location"]
        location_fields = self._get_location_fields()

        for rec in self:
            for field in location_fields:
                location_ids |= getattr(rec, field)

        location_ids.write({"is_linked_to_warehouse": True})

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._check_locations_linked_to_warehouse()
        return res

    def write(self, vals):
        """If any warehouse's location change, uncheck the old ones and check the new
        ones"""
        location_fields = self._get_location_fields()

        changed_location_ids = self.env["stock.location"]
        for rec in self:
            for loc_field in set(location_fields) & set(vals):
                changed_location_ids |= getattr(rec, loc_field)

        changed_location_ids.write({"is_linked_to_warehouse": False})

        res = super().write(vals)

        if any([loc in vals for loc in location_fields]):
            self._check_locations_linked_to_warehouse()

        return res
