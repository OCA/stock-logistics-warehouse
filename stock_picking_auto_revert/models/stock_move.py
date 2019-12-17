# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, exceptions, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_restrictions(self):
        # Restrictions before remove quants
        if self.returned_move_ids or self.split_from:
            raise exceptions.UserError(
                _("Action not allowed. Move splited / with returned moves.")
            )
        if self.move_dest_id or self.search([("move_dest_id", "=", self.id)]):
            raise exceptions.UserError(_("Action not allowed. Chained move."))
        if any(
            self.mapped("quant_ids").filtered(
                lambda x: x.qty > 0 and x.location_id != self.location_dest_id
            )
        ):
            raise exceptions.UserError(
                _(
                    "Too bad. You cannot cancel a stock move "
                    "that has been set to 'Done' and it has been moved "
                    "afterwards."
                )
            )
