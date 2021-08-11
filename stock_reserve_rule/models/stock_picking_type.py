# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    reserve_rule_ids = fields.Many2many(
        comodel_name="stock.reserve.rule",
    )
