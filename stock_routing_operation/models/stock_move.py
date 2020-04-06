# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import uuid
from itertools import chain

from psycopg2 import sql

from odoo import models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

# TODO check product_qty / product_uom_qty


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        if self.env.context.get("exclude_apply_routing_operation"):
            super()._action_assign()
        else:
            # these methods will call _action_assign in a savepoint
            # and modify the routing if necessary
            self._apply_src_move_routing_operation()
            self._apply_dest_move_routing_operation()

    def _apply_src_move_routing_operation(self):
        """Apply source routing operations

        * calls super()._action_assign() on moves not yet available
        * split the moves if their move lines have different source locations
        * apply the routing

        Important: if you inherit this method to skip the routing for some
        moves, you have to call super()._action_assign() on them
        """
        src_moves = self._split_per_src_routing_operation()
        src_moves._apply_move_location_src_routing_operation()

    def _apply_dest_move_routing_operation(self):
        """Apply destination routing operations

        * at this point, _action_assign should have been called by
          ``_apply_src_move_routing_operation``
        * split the moves if their move lines have different destination locations
        * apply the routing
        """
        dest_moves = self._split_per_dest_routing_operation()
        dest_moves._apply_move_location_dest_routing_operation()

    def _src_routing_apply_domain(self, routing):
        if not routing.src_routing_move_domain:
            return self
        domain = safe_eval(routing.src_routing_move_domain)
        return self._eval_routing_domain(domain)

    def _eval_routing_domain(self, domain):
        move_domain = [("id", "in", self.ids)]
        # Warning: if we build a domain with dotted path such as
        # group_id.is_urgent (hypothetic field), can become very slow as odoo
        # searches all "procurement.group.is_urgent" first then uses "IN
        # group_ids" on the stock move only. In such situations, it can be
        # better either to add a related field on the stock.move, either extend
        # _src_routing_apply_domain to add your own logic (based on SQL, ...).
        return self.env["stock.move"].search(expression.AND([move_domain, domain]))

    def _split_per_src_routing_operation(self):
        """Split moves per source routing operations

        When a move has move lines with different routing operations or lines
        with routing operations and lines without, on the source location, this
        method splits the move in as many source routing operations they have.

        The reason: the destination location of the moves with a routing
        operation will change and their "move_dest_ids" will be modified to
        target a new move for the routing operation.
        """
        if not self:
            return self

        new_move_per_location = {}

        savepoint_name = uuid.uuid1().hex
        self.env["base"].flush()
        # pylint: disable=sql-injection
        self.env.cr.execute(
            sql.SQL("SAVEPOINT {}").format(sql.Identifier(savepoint_name))
        )
        super()._action_assign()

        moves_with_routing = {}
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
                # TODO consider to use the domain directly in the method that
                # find the routing
                routing_picking_type = source._find_picking_type_for_routing("src")
                if not move._src_routing_apply_domain(routing_picking_type):
                    # reset to "no routing"
                    routing_picking_type = self.env["stock.picking.type"].browse()
                routing_quantities.setdefault(routing_picking_type, 0.0)
                routing_quantities[routing_picking_type] += qty

            if len(routing_quantities) > 1:
                # The whole quantity can be taken from only one location (an
                # empty routing picking type being equal to one location here),
                # nothing to split.
                moves_with_routing[move] = routing_quantities

        if not moves_with_routing:
            # no split needed, so the reservations done by _action_assign
            # are valid
            self.env["base"].flush()
            # pylint: disable=sql-injection
            self.env.cr.execute(
                sql.SQL("RELEASE SAVEPOINT {}").format(sql.Identifier(savepoint_name))
            )
            return self

        # rollack _action_assign, it'll be called again after the splits
        self.env.clear()
        # pylint: disable=sql-injection
        self.env.cr.execute(
            sql.SQL("ROLLBACK TO SAVEPOINT {}").format(sql.Identifier(savepoint_name))
        )

        for move, routing_quantities in moves_with_routing.items():
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
                    new_move_per_location[routing_location.id].append(new_move_id)

        # it is important to assign the routed moves first so they take the
        # quantities in the expected locations (same locations as the splits)
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
        super()._action_assign()
        new_moves = self.browse(chain.from_iterable(new_move_per_location.values()))
        return self + new_moves

    def _apply_move_location_src_routing_operation(self):
        """Apply routing operations

        When a move has a routing operation configured on its location and the
        destination of the move does not match the destination of the routing
        operation, this method updates the move's destination and it's picking
        type with the routing operation ones and creates a new chained move
        after it.
        """
        pickings_to_check_for_emptiness = self.env["stock.picking"]
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
            routing = source._find_picking_type_for_routing("src")
            # TODO we might optimize this by calling it once for a routing
            # and a group of moves
            if not routing or not move._src_routing_apply_domain(routing):
                continue

            if move.picking_id.picking_type_id == routing:
                # already correct
                continue

            original_destination = move.move_line_ids[0].location_dest_id

            # the current move becomes the routing move, and we'll add a new
            # move after this one to pick the goods where the routing moved
            # them, we have to unreserve and assign at the end to have the move
            # lines go to the correct destination
            move._do_unreserve()
            move.package_level_id.unlink()

            current_picking_type = move.picking_id.picking_type_id
            if self.env["stock.location"].search(
                [
                    ("id", "=", routing.default_location_dest_id.id),
                    ("id", "child_of", move.location_dest_id.id),
                ]
            ):
                # The destination of the move, as a parent of the destination
                # of the routing, goes to the correct place, but is not precise
                # enough: set the new destination to match the picking type
                move.location_dest_id = routing.default_location_dest_id
                move.picking_type_id = routing

            elif self.env["stock.location"].search(
                [
                    ("id", "=", routing.default_location_dest_id.id),
                    ("id", "parent_of", move.location_dest_id.id),
                ]
            ):
                # The destination of the move is already more precise than the
                # expected destination of the routing: keep it, but we still
                # want to change the picking type
                move.picking_type_id = routing
            else:
                # The destination of the move is unrelated (nor identical, nor
                # a parent or a child) to the routing destination: in this case
                # we have to add a routing move before the current move to
                # route the goods in the routing
                move.location_dest_id = routing.default_location_dest_id
                move.picking_type_id = routing
                # create a copy of the move with the current picking type and
                # going to its original destination: it will be assigned to the
                # same picking as the original picking of our move
                move._insert_routing_moves(
                    current_picking_type, move.location_id, original_destination
                )

            pickings_to_check_for_emptiness |= move.picking_id
            move._assign_picking()
            move._action_assign()

        pickings_to_check_for_emptiness._routing_operation_handle_empty()

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
            {"move_dest_ids": [(3, m.id) for m in dest_moves] + [(4, routing_move.id)]}
        )
        if dest_moves:
            dest_moves.write({"move_orig_ids": [(3, self.id), (4, routing_move.id)]})
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

        We don't need to cancel the reservation as done in
        ``_split_per_src_routing_operation`` because the source location
        doesn't change.
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
                    routing_picking_type = dest._find_picking_type_for_routing("dest")
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
                move_lines.modified(["product_uom_qty"])
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
            move.write({"location_dest_id": picking_type.default_location_src_id.id})
            move.move_line_ids.write(
                {"location_dest_id": picking_type.default_location_src_id.id}
            )
            move._insert_routing_moves(picking_type, move.location_dest_id, destination)
