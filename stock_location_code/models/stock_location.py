# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"
    _rec_names_search = ["complete_name", "barcode", "code"]

    code = fields.Char(
        help="Code given to this location.",
        index=True,
        copy=False,
    )

    @api.depends("name", "location_id.complete_name", "usage", "code")
    @api.depends_context("formatted_display_name")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for location in self:
            if location.code:
                location.display_name = f"[{location.code}] {location.display_name}"
        return res
