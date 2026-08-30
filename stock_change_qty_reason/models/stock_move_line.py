# Copyright 2019-2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    preset_reason_id = fields.Many2one("stock.quant.reason")
    reason = fields.Char(help="Type in a reason for the product quantity change")
