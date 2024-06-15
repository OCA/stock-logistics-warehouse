# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_linked_to_warehouse = fields.Boolean()

    is_technical_location = fields.Boolean(
        compute="_compute_is_technical_location",
        help="Technical locations will not be displayed in the simplified "
        "Locations menu, and can not be set as parent of a new location created through"
        "the simplified menu.",
        store=True,
    )

    @api.depends("location_id")
    def _compute_is_technical_location(self):
        physical_location_id = self.env.ref("stock.stock_location_locations")
        for rec in self:
            # Useful check to set 'Subcontracting Locations' as technical locations.
            rec.is_technical_location = rec.location_id == physical_location_id
