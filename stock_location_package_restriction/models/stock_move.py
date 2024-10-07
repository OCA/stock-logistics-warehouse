# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_location_package_restriction(self):
        """Check if the moves can be done regarding potential package restrictions"""
        self.filtered(
            lambda m: m.state == "done"
        ).location_dest_id._check_package_restriction()

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        self._check_location_package_restriction()
        return res
