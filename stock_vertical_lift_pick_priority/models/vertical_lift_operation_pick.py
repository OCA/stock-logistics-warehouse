# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from collections import defaultdict
from datetime import datetime
from itertools import cycle

from odoo import models


class VerticalLiftOperationPick(models.Model):
    _inherit = "vertical.lift.operation.pick"

    def _get_next_move_line(self, order):
        company = self.location_id.company_id or self.env.company
        if not company.vertical_lift_pick_by_priority:
            return super()._get_next_move_line(order)
        move_lines = self.env["stock.move.line"].search(
            self._domain_move_lines_to_do(), order=order
        )
        move_lines = self._sort_move_lines_by_demand(move_lines)
        return self._next_move_line_in_cycle(move_lines)

    def _next_move_line_in_cycle(self, move_lines):
        """Line following the current one in ``move_lines``, wrapping around.

        Same rule as ``stock_vertical_lift``, which cannot be reused because it
        builds the list and picks from it in a single method.
        """
        if not move_lines:
            return False
        current = self.current_move_line_id
        move_lines_cycle = cycle(move_lines)
        if not current or current not in move_lines:
            return next(move_lines_cycle)
        while next(move_lines_cycle) != current:
            continue
        return next(move_lines_cycle)

    def _sort_move_lines_by_demand(self, move_lines):
        """Most urgent demand first, ties keep the order given by the search.

        Skipped lines come after the others, oldest skip first. The sort is
        stable: the ``order`` passed to the search (the transfer's own
        priority and date) still decides between lines whose demand is
        equally urgent.
        """
        company = self.location_id.company_id or self.env.company
        skipped_last = company.vertical_lift_pick_skipped_last
        demand_keys = self._get_demand_sort_keys(move_lines.move_id)

        def sort_key(move_line):
            # Skipped lines must stay last, otherwise an urgent skipped line
            # would be proposed again right away and could never be skipped.
            skipped_date = skipped_last and move_line.vertical_lift_skipped_date
            if skipped_date:
                return (True, skipped_date)
            return (False, *demand_keys[move_line.move_id])

        return move_lines.sorted(sort_key)

    def _get_demand_sort_keys(self, moves):
        """Map each move to the sort key of its most urgent demand.

        The key is ``(-priority, date)``: sorting ascending gives the highest
        priority first, then the earliest scheduled date, which is the order
        Odoo itself uses to reserve moves.
        """
        return {
            move: self._demand_sort_key(demand)
            for move, demand in self._get_demand_moves(moves).items()
        }

    def _demand_sort_key(self, demand):
        if not demand:
            # Nobody waits for these goods: after every awaited line of
            # normal priority, then the search order decides.
            return (0, datetime.max)
        return min((-int(move.priority or "0"), move.date) for move in demand)

    def _get_demand_moves(self, moves):
        """Map each move to the outgoing moves waiting for its goods."""
        demand_moves = {}
        unchained = self.env["stock.move"]
        for move in moves:
            demand = self._get_chained_demand_moves(move)
            if demand:
                demand_moves[move] = demand
            else:
                unchained |= move
        if unchained:
            demand_by_product = defaultdict(lambda: self.env["stock.move"])
            for demand_move in self.env["stock.move"].search(
                self._demand_moves_domain(unchained)
            ):
                demand_by_product[demand_move.product_id] |= demand_move
            for move in unchained:
                demand_moves[move] = demand_by_product[move.product_id]
        return demand_moves

    def _get_chained_demand_moves(self, move):
        """Outgoing moves reached by following the destination moves (MTO)."""
        demand = self.env["stock.move"]
        seen = self.env["stock.move"]
        moves = move.move_dest_ids
        while moves:
            seen |= moves
            outgoing = moves.filtered(lambda m: m.picking_code == "outgoing")
            demand |= outgoing
            moves = (moves - outgoing).move_dest_ids - seen
        return demand.filtered(lambda m: m.state not in ("done", "cancel"))

    def _demand_moves_domain(self, moves):
        """Outgoing moves that may be waiting for ``moves`` goods (MTS).

        Without chaining, nothing links a replenishment to the deliveries it
        serves. Odoo's orderpoints work per warehouse, so any outgoing move of
        the same product in the same warehouse is considered a demand.
        """
        # Performance: filter first by picking type to avoid a slow database join
        picking_types = self.env["stock.picking.type"].search(
            [
                ("code", "=", "outgoing"),
                ("warehouse_id", "=", self.location_id.warehouse_id.id),
            ]
        )
        return [
            ("product_id", "in", moves.product_id.ids),
            ("picking_type_id", "in", picking_types.ids),
            ("state", "not in", ("draft", "done", "cancel")),
        ]

    def _unskip_lines_awaited_by(self, pickings):
        """Propose again the skipped lines waiting for ``pickings``.

        Called when the priority of these outgoing pickings is raised. Only
        the skipped lines of their products are looked at, so the cost stays
        low.
        """
        self.ensure_one()
        lines = self.env["stock.move.line"].search(
            self._domain_move_lines_to_do()
            + [
                ("vertical_lift_skipped_date", "!=", False),
                ("product_id", "in", pickings.move_ids.product_id.ids),
            ]
        )
        if not lines:
            return
        demand_moves = self._get_demand_moves(lines.move_id)
        awaited = lines.filtered(
            lambda line: demand_moves[line.move_id] & pickings.move_ids
        )
        awaited.write({"vertical_lift_skipped_date": False})
