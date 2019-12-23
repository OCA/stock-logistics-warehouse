# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    preset_reason_id = fields.Many2one("stock.inventory.line.reason", required=False)
