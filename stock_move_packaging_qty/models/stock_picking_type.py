# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    automatic_done_packaging_calculation = fields.Boolean(
        string="Automatically Calculate Done Packaging Quantity",
        default=True,
        help="The system calculates Done Packaging Automatically on Stock Move Lines.\n"
        "Disable this to prevent automatic calculation.",
    )
