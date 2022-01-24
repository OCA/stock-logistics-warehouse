# Copyright 2022 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    manual_cost = fields.Float(
        string="Manual Cost",
    )

    def _get_price_unit(self):
        return self.manual_cost or super()._get_price_unit()
