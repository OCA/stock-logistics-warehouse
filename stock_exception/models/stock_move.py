# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = ["stock.move", "base.exception.method"]
    _name = "stock.move"

    ignore_exception = fields.Boolean(
        related="picking_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("picking_id")

    @api.model
    def _reverse_field(self):
        return "picking_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("picking_id")
