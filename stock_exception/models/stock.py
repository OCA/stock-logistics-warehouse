# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = ["stock.picking", "base.exception"]
    _name = "stock.picking"
    _order = "main_exception_id asc, priority desc, scheduled_date asc, id desc"

    @api.model
    def test_all_draft_pickings(self):
        picking_set = self.search([("state", "=", "draft")])
        picking_set.detect_exceptions()
        return True

    @api.model
    def _reverse_field(self):
        return "picking_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        moves = self.mapped("move_lines")
        all_exceptions += moves.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "move_lines", "state")
    def stock_check_exception(self):
        pickings = self.filtered(
            lambda s: s.state in ["waiting", "confirmed", "assigned"]
        )
        if pickings:
            pickings._check_exception()

    @api.onchange("move_lines")
    def onchange_ignore_exception(self):
        if self.state in ["waiting", "confirmed", "assigned"]:
            self.ignore_exception = False

    def action_confirm(self):
        if self.detect_exceptions() and not self.ignore_exception:
            return self._popup_exceptions()
        return super().action_confirm()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref("stock_exception.action_stock_exception_confirm")
        return action
