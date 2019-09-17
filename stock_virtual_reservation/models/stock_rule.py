# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    # TODO add in view, visible when action is pull
    virtual_reservation_defer_pull = fields.Boolean(
        string="Defer Pull using Virtual Reservation",
        default=False,
        help="Create the pull moves only when the virtual "
        "reservation is > 0.",
    )

    def _run_pull(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
    ):
        if (
            self.virtual_reservation_defer_pull
            # we generate the destination operation
            # TODO is there a reason for this? Why not
            # generate them when available too?
            and not self.picking_type_id.code == "outgoing"
        ):
            return True
        return super()._run_pull(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            values,
        )
