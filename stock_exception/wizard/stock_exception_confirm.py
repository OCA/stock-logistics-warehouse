# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockExceptionConfirm(models.TransientModel):
    _name = "stock.exception.confirm"
    _description = "Stock exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one("stock.picking", "Stock Picking")

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
            self.related_model_id.action_confirm()
        return super().action_confirm()
