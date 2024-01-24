# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, exceptions, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_restrictions(self):
        # Restrictions before remove quants
        if self.returned_move_ids:
            raise exceptions.UserError(
                _("Action not allowed. Move splited / with returned moves.")
            )
        if self.move_dest_ids or self.search([("move_dest_ids", "in", self.ids)]):
            raise exceptions.UserError(_("Action not allowed. Chained move."))
