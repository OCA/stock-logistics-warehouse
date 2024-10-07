# Copyright (C) 2019 Akretion
# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    warehouse_id = fields.Many2one(
        "stock.warehouse", related="move_id.warehouse_id", store=True, index=True
    )
