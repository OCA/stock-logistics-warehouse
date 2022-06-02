# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    def action_cancel(self):
        if not self.filtered("cancel_confirm"):
            return self.open_cancel_confirm_wizard()
        res = super().action_cancel()
        # Ensure to cancel the picking w/o moves that wasn't cancelled by odoo core
        self.filtered(lambda l: l.state != "cancel" and not l.move_lines).write(
            {"state": "cancel"}
        )
        return res
