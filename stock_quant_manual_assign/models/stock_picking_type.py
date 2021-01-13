# Copyright 2021 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    auto_fill_qty_done = fields.Boolean(
        "Auto-fill Quantity Done",
        help="Select this in case done quantity of the stock move line should "
        "be auto-filled when quants are manually assigned.",
    )
