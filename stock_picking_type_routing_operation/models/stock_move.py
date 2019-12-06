# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from itertools import chain
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        super()._action_assign()
        if not self.env.context.get("exclude_apply_routing_operation"):
            self._apply_src_move_routing_operation()
            self._apply_dest_move_routing_operation()

    def _apply_src_move_routing_operation(self):
        src_moves = self._split_per_src_routing_operation()
        src_moves._apply_move_location_src_routing_operation()

    def _apply_dest_move_routing_operation(self):
        dest_moves = self._split_per_dest_routing_operation()
        dest_moves._apply_move_location_dest_routing_operation()

    def _split_per_src_routing_operation(self):
        """Split moves per source routing operations

        When a move has move lines with different routing operations or lines
        with routing operations and lines without, on the source location, this
        method split the move in as many source routing operations they have.

        The reason: the destination location of the moves with a routing
        operation will change and their "move_dest_ids" will be modified to
        target a new move for the routing operation.
        """
        move_to_assign_ids = set()
        new_move_per_location = {}
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            # Group move lines per source location, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            move_lines = {}
            for move_line in move.move_line_ids:
                location = move_line.location_id
                move_lines[location] = sum(move_line.mapped("product_uom_qty"))

            # We'll split the move to have one move per different location
            # where we have to take products
            routing_quantities = {}
            for source, qty in move_lines.items():
                routing_picking_type = source._find_picking_type_for_routing(
                    "src"
                )
                routing_quantities.setdefault(routing_picking_type, 0.0)
                routing_quantities[routing_picking_type] += qty

            if len(routing_quantities) == 1:
                # The whole quantity can be taken from only one location (an
                # empty routing picking type being equal to one location here),
                # nothing to split.
                continue

            move._do_unreserve()
            move.package_level_id.unlink()
            move_to_assign_ids.add(move.id)
            for picking_type, qty in routing_quantities.items():
                # When picking_type is empty, it means we have no routing
                # operation for the move, so we have nothing to do.
                if picking_type:
                    routing_location = picking_type.default_location_src_id
                    # If we have a routing operation, the move may have several
                    # lines with different routing operations (or lines with
                    # a routing operation, lines without). We split the lines
                    # according to these.
                    # The _split() method returns the same move if the qty
                    # is the same than the move's qty, so we don't need to
                    # explicitly check if we really need to split or not.
                    new_move_id = move._split(qty)
                    new_move_per_location.setdefault(routing_location.id, [])
                    new_move_per_location[routing_location.id].append(
                        new_move_id
                    )

        # it is important to assign the routed moves first
        for location_id, new_move_ids in new_move_per_location.items():
            new_moves = self.browse(new_move_ids)
            new_moves.with_context(
                # Prevent to call _apply_move_location_routing_operation, will
                # be called when all lines are processed.
                exclude_apply_routing_operation=True,
                # Force reservation of quants in the location they were
                # reserved in at the origin (so we keep the same quantities
                # at the same places)
                gather_in_location_id=location_id,
            )._action_assign()

        # reassign the moves which have been unreserved for the split
        moves_to_assign = self.browse(move_to_assign_ids)
        if moves_to_assign:
            moves_to_assign._action_assign()
        new_moves = self.browse(
            chain.from_iterable(new_move_per_location.values())
        )
        return self + new_moves

    def _apply_move_location_src_routing_operation(self):
        """Apply routing operations

        When a move has a routing operation configured on its location and the
        destination of the move does not match the destination of the routing
        operation, this method updates the move's destination and it's picking
        type with the routing operation ones and creates a new chained move
        after it.
        """
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            # Group move lines per source location, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            # At this point, we should not have lines with different source
            # locations, they have been split in
            # _split_per_routing_operation(), so we can take the first one
            source = move.move_line_ids[0].location_id
            destination = move.move_line_ids[0].location_dest_id
            # we have to add a move as destination
            # we have to add move as origin
            routing = source._find_picking_type_for_routing("src")
            if not routing:
                continue

            if self.env["stock.location"].search(
                [
                    ("id", "=", routing.default_location_dest_id.id),
                    ("id", "parent_of", move.location_dest_id.id),
                ]
            ):
                # we don't need to do anything because we already go through
                # the expected destination
                continue

            # the current move becomes the routing move, and we'll add a new
            # move after this one to pick the goods where the routing moved
            # them, we have to unreserve and assign at the end to have the move
            # lines go to the correct destination
            move._do_unreserve()
            move.package_level_id.unlink()
            dest = routing.default_location_dest_id
            current_picking_type = move.picking_id.picking_type_id
            move.write(
                {"location_dest_id": dest.id, "picking_type_id": routing.id}
            )
            move._insert_routing_moves(
                current_picking_type, move.location_id, destination
            )

            picking = move.picking_id
            move._assign_picking()
            if not picking.move_lines:
                # When the picking type changes, it will create a new picking
                # for the move. If the previous picking has no other move,
                # we have to drop it.
                picking.unlink()

            move._action_assign()

    def _insert_routing_moves(self, picking_type, location, destination):
        """Create a chained move for the source routing operation"""
        self.ensure_one()
        dest_moves = self.move_dest_ids
        # Insert move between the source and destination for the new
        # operation
        routing_move_values = self._prepare_routing_move_values(
            picking_type, location, destination
        )
        routing_move = self.copy(routing_move_values)

        # modify the chain to include the new move
        self.write(
            {
                "move_dest_ids": [(3, m.id) for m in dest_moves]
                + [(4, routing_move.id)]
            }
        )
        if dest_moves:
            dest_moves.write(
                {"move_orig_ids": [(3, self.id), (4, routing_move.id)]}
            )
        routing_move._action_confirm(merge=False)
        routing_move._assign_picking()

    def _prepare_routing_move_values(self, picking_type, source, destination):
        return {
            "picking_id": False,
            "location_id": source.id,
            "location_dest_id": destination.id,
            "state": "waiting",
            "picking_type_id": picking_type.id,
        }

    def _split_per_dest_routing_operation(self):
        """Split moves per destination routing operations

        When a move has move lines with different routing operations or lines
        with routing operations and lines without, on the destination, this
        method split the move in as many destination routing operations they
        have.

        The reason: the destination location of the moves with a routing
        operation will change and their "move_dest_ids" will be modified to
        target a new move for the routing operation.
        """
        new_moves = self.browse()
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            # Group move lines per destination location, some may need an
            # additional operations while others not. Store the number of
            # products to take from each location, so we'll be able to split
            # the move if needed.
            routing_move_lines = {}
            routing_operations = {}
            for move_line in move.move_line_ids:
                dest = move_line.location_dest_id
                if dest in routing_operations:
                    routing_picking_type = routing_operations[dest]
                else:
                    routing_picking_type = dest._find_picking_type_for_routing(
                        "dest"
                    )
                routing_move_lines.setdefault(
                    routing_picking_type, self.env["stock.move.line"].browse()
                )
                routing_move_lines[routing_picking_type] |= move_line

            if len(routing_move_lines) == 1:
                # If we have no routing operation or only one routing
                # operation, we don't need to split the moves. We need to split
                # only if we have 2 different routing operations, or move
                # without routing operation and one(s) with routing operations.
                continue

            for picking_type, move_lines in routing_move_lines.items():
                if not picking_type:
                    # No routing operation is required for these moves,
                    # continue to the next
                    continue
                # if we have a picking type, split returns the same move if
                # the qty is the same
                qty = sum(move_lines.mapped("product_uom_qty"))
                new_move_id = move._split(qty)
                new_move = self.browse(new_move_id)
                move_lines.write({"move_id": new_move.id})
                assert move.state in ("assigned", "partially_available")
                # We know the new move is 'assigned' because we created it
                # with the quantity matching the move lines that we move into
                new_move.state = "assigned"
                new_moves += new_move

        return self + new_moves

    def _apply_move_location_dest_routing_operation(self):
        """Apply routing operations

        When a move has a routing operation configured on its location and the
        destination of the move does not match the destination of the routing
        operation, this method updates the move's destination and it's picking
        type with the routing operation ones and creates a new chained move
        after it.
        """
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            # Group move lines per source location, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            # At this point, we should not have lines with different source
            # locations, they have been split in
            # _split_per_routing_operation(), so we can take the first one
            destination = move.move_line_ids[0].location_dest_id
            picking_type = destination._find_picking_type_for_routing("dest")
            if not picking_type:
                continue

            if self.env["stock.location"].search(
                [
                    ("id", "=", picking_type.default_location_src_id.id),
                    ("id", "parent_of", move.location_id.id),
                ]
            ):
                # This move has been created for the routing operation,
                # or was already created with the correct locations anyway,
                # exit or it would indefinitely add a next move
                continue

            # Move the goods in the "routing" location instead.
            # In this use case, we want to keep the move lines so we don't
            # change the reservation.
            move.write(
                {"location_dest_id": picking_type.default_location_src_id.id}
            )
            move.move_line_ids.write(
                {"location_dest_id": picking_type.default_location_src_id.id}
            )
            move._insert_routing_moves(
                picking_type, move.location_dest_id, destination
            )
