# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    line_accuracy = fields.Float(
        string="Accuracy",
        store=True,
    )
    theoretical_qty = fields.Float(string="Theoretical Quantity", store=True)
    counted_qty = fields.Float(string="Counted Quantity", store=True)
