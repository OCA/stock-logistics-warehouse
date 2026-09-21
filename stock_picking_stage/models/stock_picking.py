# Copyright 2025 Camptocamp SA
# @author: Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stage_id = fields.Many2one("stock.picking.stage", index=True, tracking=True)
    stage_code = fields.Char(related="stage_id.code")
    stage_color = fields.Integer(related="stage_id.color")
