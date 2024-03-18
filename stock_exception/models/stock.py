# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = ["stock.picking", "base.exception"]
    _name = "stock.picking"

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
        moves = self.mapped("move_ids")
        all_exceptions += moves.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "move_ids", "state")
    def stock_check_exception(self):
        pickings = self.filtered(
            lambda s: s.state in ["waiting", "confirmed", "assigned"]
        )
        if pickings:
            pickings._check_exception()

    @api.onchange("move_ids")
    def onchange_ignore_exception(self):
        if self.state in ["waiting", "confirmed", "assigned"]:
            self.ignore_exception = False

    def action_confirm(self):
        for rec in self:
            if rec.detect_exceptions() and not rec.ignore_exception:
                return rec._popup_exceptions()
        return super().action_confirm()

    def button_validate(self):
        for rec in self:
            if rec.detect_exceptions() and not rec.ignore_exception:
                if rec.exception_ids.check_on_validate:
                    raise ValidationError("\n".join(rec.exception_ids.mapped("name")))
        return super().button_validate()

    @api.model
    def _get_popup_action(self):
        action = self.env.ref("stock_exception.action_stock_exception_confirm")
        return action

    def _check_exception(self):
        if not self.env.context.get("check_exception", True):
            return True
        exception_ids = self.detect_exceptions()
        if exception_ids and self.env.context.get("raise_exception", True):
            exceptions = self.env["exception.rule"].browse(exception_ids)
            for picking in exceptions.picking_ids:
                if exceptions.check_on_confirm == True and picking.state == 'assigned':
                    raise ValidationError("\n".join(exceptions.mapped("name")))
                if exceptions.check_on_validate == True and picking.state == 'done':
                    raise ValidationError("\n".join(exceptions.mapped("name")))
