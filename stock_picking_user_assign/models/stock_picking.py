# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_assign_to_me(self):
        if self.filtered("user_id"):
            raise UserError(_("Picking has already a responsible assigned"))
        self.user_id = self.env.user
        if self.env.context.get("assign_user_and_open_form", False) and len(self) == 1:
            return self.get_formview_action()
