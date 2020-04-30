# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    canceled_by_routing = fields.Boolean(
        default=False,
        help="Technical field. Indicates the transfer is"
        " canceled because it was left empty after a dynamic routing.",
    )

    @api.depends("canceled_by_routing")
    def _compute_state(self):
        super()._compute_state()
        for picking in self:
            if picking.canceled_by_routing:
                picking.state = "cancel"

    def _dynamic_routing_handle_empty(self):
        """Handle pickings emptied during a dynamic routing"""
        for picking in self:
            if not picking.move_lines:
                # When the picking type changes, it will create a new picking
                # for the move. As the picking is now empty, it's useless.
                # We could drop it but it can make code crash later in the
                # transaction. This flag will set the picking as cancel.
                picking.canceled_by_routing = True
