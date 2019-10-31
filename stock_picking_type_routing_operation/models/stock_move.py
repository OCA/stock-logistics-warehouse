# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from itertools import chain
from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        super()._action_assign()
        if not self.env.context.get('exclude_apply_routing_operation'):
            src_moves = self._split_per_routing_operation()
            src_moves._apply_move_location_routing_operation()
            dest_moves = self._split_per_dest_routing_operation()
            dest_moves._apply_move_location_dest_routing_operation()

    def _split_per_dest_routing_operation(self):
        move_to_assign_ids = set()
        new_move_per_location = {}
        for move in self:
            if move.state not in ('assigned', 'partially_available'):
                continue

            # Group move lines per source location, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            move_lines = {}
            for move_line in move.move_line_ids:
                location = move_line.location_dest_id
                move_lines[location] = sum(move_line.mapped('product_uom_qty'))

            # We'll split the move to have one move per different location
            # where we have to take products
            routing_quantities = {}
            for dest_location, qty in move_lines.items():
                routing_picking_type = \
                    dest_location._find_picking_type_for_routing("dest")
                routing_quantities.setdefault(routing_picking_type, 0.0)
                routing_quantities[routing_picking_type] += qty

            if len(routing_quantities) == 1:
                # The whole quantity can be taken from only one location (an
                # empty routing picking type being equal to one location here),
                # nothing to split.
                continue

            move._do_unreserve()
            move_to_assign_ids.add(move.id)
            for picking_type, qty in routing_quantities.items():
                # if picking type is empty, we don't need a new move
                # not a zone
                if picking_type:
                    routing_location = picking_type.default_location_src_id
                    # if we have a picking type, split returns the same move if
                    # the qty is the same
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
        new_moves = self.browse(chain.from_iterable(
            new_move_per_location.values()
        ))
        return self + new_moves

    def _split_per_routing_operation(self):
        """Split moves per routing operations

        When a move has move lines with different routing operations or lines
        with routing operations and lines without, this method split the move
        in as many routing operations they have. The reason, the destination
        location of the moves with a routing operation will change and their
        "move_dest_ids" will be modified to target a new intermediary move (for
        the routing operation).
        """
        move_to_assign_ids = set()
        new_move_per_location = {}
        for move in self:
            if move.state not in ('assigned', 'partially_available'):
                continue

            # Group move lines per source location, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            move_lines = {}
            for move_line in move.move_line_ids:
                location = move_line.location_id
                move_lines[location] = sum(move_line.mapped('product_uom_qty'))

            # We'll split the move to have one move per different location
            # where we have to take products
            routing_quantities = {}
            for source_location, qty in move_lines.items():
                routing_picking_type = \
                    source_location._find_picking_type_for_routing("src")
                routing_quantities.setdefault(routing_picking_type, 0.0)
                routing_quantities[routing_picking_type] += qty

            if len(routing_quantities) == 1:
                # The whole quantity can be taken from only one location (an
                # empty routing picking type being equal to one location here),
                # nothing to split.
                continue

            move._do_unreserve()
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
        new_moves = self.browse(chain.from_iterable(
            new_move_per_location.values()
        ))
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
            if move.state not in ('assigned', 'partially_available'):
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
            if (
                move.location_id == picking_type.default_location_src_id and
                # a predecessor move is a "routing operation"
                move.move_orig_ids.filtered(
                    lambda o: o.picking_type_id == picking_type
                )
            ):
                # already done
                continue

            move._do_unreserve()
            move.write({
                'location_id': picking_type.default_location_src_id.id,
                'state': 'waiting',
                # 'picking_type_id': picking_type.id,
            })

            move._insert_dest_middle_moves(picking_type)

    def _apply_move_location_routing_operation(self):
        """Apply routing operations

        When a move has a routing operation configured on its location and the
        destination of the move does not match the destination of the routing
        operation, this method updates the move's destination and it's picking
        type with the routing operation ones and creates a new chained move
        after it.
        """
        for move in self:
            if move.state not in ('assigned', 'partially_available'):
                continue

            # Group move lines per source location, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            # At this point, we should not have lines with different source
            # locations, they have been split in
            # _split_per_routing_operation(), so we can take the first one
            source = move.move_line_ids[0].location_id
            picking_type = source._find_picking_type_for_routing("src")
            if not picking_type:
                continue
            if (
                move.picking_type_id == picking_type and
                move.location_dest_id == picking_type.default_location_dest_id
            ):
                # already done
                continue

            move._do_unreserve()
            move.write({
                'location_dest_id': picking_type.default_location_dest_id.id,
                'picking_type_id': picking_type.id,
            })
            move._insert_middle_moves()
            move._assign_picking()
            move._action_assign()

    def _insert_middle_moves(self):
        """Create a chained move for the routing operation"""
        self.ensure_one()
        dest_moves = self.move_dest_ids
        dest_location = self.location_dest_id
        for dest_move in dest_moves:
            final_location = dest_move.location_id
            if dest_location == final_location:
                # shortcircuit to avoid a query checking if it is a child
                continue
            child_locations = self.env['stock.location'].search([
                ('id', 'child_of', final_location.id)
            ])
            if dest_location in child_locations:
                # normal behavior, we don't need a move between A and B
                continue
            # Insert move between the source and destination for the new
            # operation
            middle_move_values = self._prepare_middle_move_values(
                final_location
            )
            middle_move = self.copy(middle_move_values)
            dest_move.write({
                'move_orig_ids': [(3, self.id), (4, middle_move.id)],
            })
            self.write({
                'move_dest_ids': [(3, dest_move.id), (4, middle_move.id)],
            })
            middle_move._action_confirm(merge=False)

    def _prepare_middle_move_values(self, destination):
        return {
            'picking_id': False,
            'location_id': self.location_id.id,
            'location_dest_id': destination.id,
            'state': 'waiting',
            'picking_type_id': self.picking_id.picking_type_id.id,
        }

    def _insert_dest_middle_moves(self, picking_type):
        """Create a chained move for the routing operation"""
        self.ensure_one()
        source_moves = self.move_orig_ids
        source_location = self.location_id
        for source_move in source_moves:
            previous_location = source_move.location_dest_id
            if source_location == previous_location:
                continue
            # Insert a move between the previous move and the source of our
            # move as their locations do not match.
            middle_move_values = self._prepare_dest_middle_move_values(
                picking_type,
                previous_location
            )
            middle_move = self.copy(middle_move_values)
            source_move.write({
                'move_dest_ids': [(3, self.id), (4, middle_move.id)],
            })
            self.write({
                'move_orig_ids': [(3, source_move.id), (4, middle_move.id)],
            })
            middle_move._action_confirm(merge=False)
            middle_move._assign_picking()
            middle_move._action_assign()

    def _prepare_dest_middle_move_values(self, picking_type, source):
        return {
            'picking_id': False,
            'location_id': source.id,
            'location_dest_id': self.location_id.id,
            'state': 'waiting',
            'picking_type_id': picking_type.id,
        }
