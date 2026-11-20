# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    wh_lock_stock_loc_id = fields.Many2one(
        comodel_name="stock.location",
        string="Lock Location",
        domain=[("usage", "=", "internal")],
        check_company=True,
        help="Warehouse location holding the locked stock.",
    )

    def _get_locations_values(self, vals, code=False):
        # OVERRIDE: create the lock location with the other warehouse locations.
        locations = super()._get_locations_values(vals, code=code)
        company_id = vals.get(
            "company_id", self.default_get(["company_id"])["company_id"]
        )
        code = vals.get("code") or code or ""
        code = code.replace(" ", "").upper()
        locations["wh_lock_stock_loc_id"] = {
            "name": self.env._("Lock"),
            "active": True,
            "usage": "internal",
            "barcode": self._valid_barcode(code + "LOCK", company_id),
        }
        return locations
