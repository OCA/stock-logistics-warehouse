# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    barcode_report_visible = fields.Boolean(
        related="picking_type_id.display_report_picking_barcode",
    )
