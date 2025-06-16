# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models
from odoo.osv.expression import AND

from odoo.addons.stock_location_pending_move.models.stock_location import (
    PENDING_MOVE_DOMAIN,
)


class StockLocation(models.Model):

    _inherit = "stock.location"

    exclude_from_fill_state_computation = fields.Boolean(
        help="Don't compute the fill state for this location. Checking this on"
        "intensively used locations can improve performances."
    )
    fill_state = fields.Selection(
        selection=[
            ("empty", "Empty"),
            ("filled", "Filled"),
            ("being_filled", "Being Filled"),
            ("being_emptied", "Being Emptied"),
        ],
        compute="_compute_fill_state",
        store=True,
        index=True,
        help="""
        This shows the location fill state.
        Possible values:
        [empty] Empty location
        [filled] Filled location
        [being_filled] The location is empty and an incoming move is in progress
        [being_emptied] The location is filled and the outgoing move(s) will empty the location
        """,
    )

    def _get_locations_for_fill_state(self):
        """
        Filter the locations to compute the fill state
        as some contain too much quants to be efficient (customers/suppliers).
        Filter explicitly excluded locations too.
        """
        return self.filtered(
            lambda location: not location.exclude_from_fill_state_computation
            and location.usage not in ["customer", "supplier"]
        )

    def _get_quant_fill_state_domain(self):
        """
        This will help building the domain to retrieve quants
        to compute the fill state of their locations.
        """
        return [("location_id", "in", self.ids)]

    @api.depends(
        "quant_ids.quantity",
        "pending_out_move_line_ids.qty_done",
        "pending_in_move_ids",
        "pending_in_move_line_ids",
    )
    def _compute_fill_state(self):
        """ """
        locations_to_compute = self._get_locations_for_fill_state()
        location_domain = locations_to_compute._get_quant_fill_state_domain()
        out_qty_by_location = {}
        qty_by_location = {}
        domain = AND([PENDING_MOVE_DOMAIN, location_domain])
        for group in self.env["stock.move.line"].read_group(
            domain,
            fields=["qty_done:sum"],
            groupby=["location_id"],
        ):
            location_id = group["location_id"][0]
            out_qty_by_location[location_id] = group["qty_done"]
        for group in self.env["stock.quant"].read_group(
            location_domain, fields=["quantity:sum"], groupby=["location_id"]
        ):
            location_id = group["location_id"][0]
            qty_by_location[location_id] = group["quantity"]
        records_by_state = defaultdict(lambda: self.browse())
        # As field is stored, we can exclude records from compute loop
        for rec in locations_to_compute:
            qty_in_location = qty_by_location.get(rec.id, 0.0)
            out_by_location = out_qty_by_location.get(rec.id, 0.0)
            if (
                out_by_location
                and (qty_in_location - out_by_location <= 0)
                and not (rec.pending_in_move_ids or rec.pending_in_move_line_ids)
            ):
                records_by_state["being_emptied"] |= rec
            elif (qty_in_location - out_by_location <= 0) and (
                rec.pending_in_move_ids or rec.pending_in_move_line_ids
            ):
                records_by_state["being_filled"] |= rec
            elif qty_in_location > 0.0:
                records_by_state["filled"] |= rec
            else:
                records_by_state["empty"] |= rec

        for state, records in records_by_state.items():
            # Don't update if value is already set
            records.filtered(
                lambda record: record.fill_state != state
            ).fill_state = state
