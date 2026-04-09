# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    display_report_picking_barcode = fields.Boolean(
        help="Check this if you want to display the picking barcode "
        "on the delivery slip report",
    )
