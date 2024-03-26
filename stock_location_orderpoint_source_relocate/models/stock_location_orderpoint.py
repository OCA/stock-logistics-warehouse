# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import float_round


class StockLocationOrderpoint(models.Model):
    _inherit = "stock.location.orderpoint"

    @api.model
    def _compute_quantities_dict(self, locations, products):
        qties = super()._compute_quantities_dict(locations, products)
        # With the source relocation, we could have stock on the location that
        # is reserved by moves with a source location on the parent location.
        # Those moves are not considered by the standard virtual available
        # stock.
        Move = self.env["stock.move"].with_context(active_test=False)
        for location, location_dict in qties.items():
            products = products.with_context(location=location.id)
            _, _, domain_move_out_loc = products._get_domain_locations()
            domain_move_out_loc_todo = [
                (
                    "state",
                    "in",
                    ("waiting", "confirmed", "assigned", "partially_available"),
                )
            ] + domain_move_out_loc
            for product, qty in location_dict.items():
                moves = Move.search(
                    domain_move_out_loc_todo + [("product_id", "=", product.id)],
                    order="id",
                )
                rounding = product.uom_id.rounding
                unreserved_availability = float_round(
                    qty["outgoing_qty"] - sum(m.reserved_availability for m in moves),
                    precision_rounding=rounding,
                )
                qty["virtual_available"] = float_round(
                    qty["free_qty"] + qty["incoming_qty"] - unreserved_availability,
                    precision_rounding=rounding,
                )

        return qties
