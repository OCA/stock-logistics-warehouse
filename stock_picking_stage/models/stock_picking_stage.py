# Copyright 2025 Camptocamp SA
# @author: Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from random import randint

from odoo import fields, models


class StockPickingStage(models.Model):
    _name = "stock.picking.stage"
    _description = "Picking Stage"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True, copy=False)
    code = fields.Char(copy=False)
    color = fields.Integer("Color Index", default=_get_default_color, copy=False)
