# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockRequestOrder(models.Model):
    _name = "stock.request.order"
    _inherit = ["stock.request.order", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    def action_cancel(self):
        if not self.filtered("cancel_confirm") and not self.env.context.get(
            "bypass_confirm_wizard"
        ):
            return self.open_cancel_confirm_wizard()
        return super().action_cancel()

    def action_draft(self):
        self.clear_cancel_confirm_data()
        return super().action_draft()
