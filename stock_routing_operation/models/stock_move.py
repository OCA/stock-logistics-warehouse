# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import uuid
from itertools import chain

from psycopg2 import sql

from odoo import fields, models

# TODO check product_qty / product_uom_qty


class StockMove(models.Model):
    _inherit = "stock.move"

    pull_routing_rule_id = fields.Many2one(
        comodel_name="stock.routing.rule",
        copy=False,
        help="Technical field. Store the routing pull rule that has been"
        " selected for the move.",
    )
    push_routing_rule_id = fields.Many2one(
        comodel_name="stock.routing.rule",
        copy=False,
        help="Technical field. Store the routing push rule that has been"
        " selected for the move.",
    )

    def _action_assign(self):
        if self.env.context.get("exclude_apply_routing_operation"):
            super()._action_assign()
        else:
            # these methods will call _action_assign in a savepoint
            # and modify the routing if necessary
            self._split_and_apply_routing_pull()
            self._split_and_apply_routing_push()

    def _split_and_apply_routing_pull(self):
        """Apply source routing operations

        * calls super()._action_assign() on moves not yet available
        * split the moves if their move lines have different source locations
        * apply the routing

        Important: if you inherit this method to skip the routing for some
        moves, you have to call super()._action_assign() on them
        """
        src_moves = self._split_and_set_rule_for_routing_pull()
        src_moves._apply_routing_rule_pull()

    def _split_and_apply_routing_push(self):
        """Apply destination routing operations

        * at this point, _action_assign should have been called by
          ``_split_and_apply_routing_pull``
        * split the moves if their move lines have different destination locations
        * apply the routing
        """
        dest_moves = self._split_and_set_rule_for_routing_push()
        dest_moves._apply_routing_rule_push()

    def _split_and_set_rule_for_routing_pull(self):
        """Split moves per source routing operations

        When a move has move lines with different routing operations or lines
        with routing operations and lines without, on the source location, this
        method splits the move in as many source routing operations they have.

        The reason: the destination location of the moves with a routing
        operation will change and their "move_dest_ids" will be modified to
        target a new move for the routing operation.

        This method writes "pull_routing_rule_id" on the moves, this rule will be
        used by ``_apply_routing_rule_pull``
        """
        if not self:
            return self

        savepoint_name = uuid.uuid1().hex
        self.env["base"].flush()
        # pylint: disable=sql-injection
        self.env.cr.execute(
            sql.SQL("SAVEPOINT {}").format(sql.Identifier(savepoint_name))
        )
        super()._action_assign()

        move_routing_rules = self.env["stock.routing"]._routing_rule_for_moves(
            "pull", self
        )
        moves_routing = {}
        no_routing_rule = self.env["stock.routing.rule"].browse()
        need_split = False
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            # Group move lines per their rule, some may need an additional
            # operations while others not. Store the number of products to
            # take from each location, so we'll be able to split the move
            # if needed.
            routing_rules = move_routing_rules[move]
            moves_routing[move] = {
                rule: sum(move_lines.mapped("product_uom_qty"))
                for rule, move_lines in routing_rules.items()
            }
            if move.state == "partially_available":
                # consider unreserved quantity as without routing, so it will
                # be split if another part of the quantity need a routing
                moves_routing[move].setdefault(no_routing_rule, 0)
                moves_routing[move][no_routing_rule] += (
                    move.product_uom_qty - move.reserved_availability
                )

        if any(len(rules) > 1 for rules in moves_routing.values()):
            need_split = True
        else:
            # shortcut, we can directly save the rule as we do not need
            # to split
            for move, rule_quantities in moves_routing.items():
                move.pull_routing_rule_id = next(iter(rule_quantities))

        if not need_split:
            # no split needed, so the reservations done by _action_assign
            # are valid
            self.env["base"].flush()
            # pylint: disable=sql-injection
            self.env.cr.execute(
                sql.SQL("RELEASE SAVEPOINT {}").format(sql.Identifier(savepoint_name))
            )
            return self

        # rollback _action_assign, it'll be called again after the splits
        self.env.clear()
        # pylint: disable=sql-injection
        self.env.cr.execute(
            sql.SQL("ROLLBACK TO SAVEPOINT {}").format(sql.Identifier(savepoint_name))
        )

        new_move_per_location = {}
        for move, routing_quantities in moves_routing.items():
            for routing_rule, qty in routing_quantities.items():
                # When the rule is empty, it means we have no routing
                # operation for the move, so we have nothing to do,
                # it will behave as normally.
                if not routing_rule:
                    continue
                routing_location = routing_rule.location_src_id
                # If we have a routing operation, the move may have several
                # lines with different routing operations (or lines with
                # a routing operation, lines without). We split the lines
                # according to these.
                # The _split() method returns the same move if the qty
                # is the same than the move's qty, so we don't need to
                # explicitly check if we really need to split or not.
                new_move_id = move._split(qty)
                new_move = self.env["stock.move"].browse(new_move_id)
                new_move.pull_routing_rule_id = routing_rule
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

    def _apply_routing_rule_pull(self):
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
            routing_rule = move.pull_routing_rule_id
            if not routing_rule:
                continue
            if move.picking_id.picking_type_id == routing_rule.picking_type_id:
                # already correct
                continue

            # we expect all the lines to go to the same destination for
            # pull routing rules
            original_destination = move.move_line_ids[0].location_dest_id

            # the current move becomes the routing move, and we'll add a new
            # move after this one to pick the goods where the routing moved
            # them, we have to unreserve and assign at the end to have the move
            # lines go to the correct destination
            move.mapped("move_line_ids.package_level_id").unlink()
            move._do_unreserve()

            current_picking_type = move.picking_id.picking_type_id
            if self.env["stock.location"].search(
                [
                    ("id", "=", routing_rule.location_dest_id.id),
                    ("id", "child_of", move.location_dest_id.id),
                ]
            ):
                # The destination of the move, as a parent of the destination
                # of the routing, goes to the correct place, but is not precise
                # enough: set the new destination to match the rule's one
                move.location_id = routing_rule.location_src_id
                move.location_dest_id = routing_rule.location_dest_id
                move.picking_type_id = routing_rule.picking_type_id

            elif self.env["stock.location"].search(
                [
                    ("id", "=", routing_rule.location_dest_id.id),
                    ("id", "parent_of", move.location_dest_id.id),
                ]
            ):
                # The destination of the move is already more precise than the
                # expected destination of the routing: keep it, but we still
                # want to change the picking type
                move.location_id = routing_rule.location_src_id
                move.picking_type_id = routing_rule.picking_type_id
            else:
                # The destination of the move is unrelated (nor identical, nor
                # a parent or a child) to the routing destination: in this case
                # we have to add a routing move before the current move to
                # route the goods in the routing
                source_location = move.location_id
                move.location_id = routing_rule.location_src_id
                move.location_dest_id = routing_rule.location_dest_id
                move.picking_type_id = routing_rule.picking_type_id
                # create a copy of the move with the current picking type and
                # going to its original destination: it will be assigned to the
                # same picking as the original picking of our move
                move._insert_routing_moves(
                    current_picking_type, source_location, original_destination
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

    def _split_and_set_rule_for_routing_push(self):
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
        move_routing_rules = self.env["stock.routing"]._routing_rule_for_moves(
            "push", self
        )
        for move in self:
            if move.state not in ("assigned", "partially_available"):
                continue

            routing_rules = move_routing_rules[move]

            if len(routing_rules) == 1:
                # If we have no routing operation or only one routing
                # operation, we don't need to split the moves. We need to split
                # only if we have 2 different routing operations, or move
                # without routing operation and one(s) with routing operations.
                rule = next(iter(routing_rules))
                if rule:
                    # but if we have a rule, store it to apply it later
                    move.push_routing_rule_id = rule
                continue

            for rule, move_lines in routing_rules.items():
                if not rule:
                    # No routing operation is required for these moves,
                    # continue to the next
                    continue
                # if we have a routing rule, split returns the same move if
                # the qty is the same
                qty = sum(move_lines.mapped("product_uom_qty"))
                new_move_id = move._split(qty)
                new_move = self.browse(new_move_id)
                move_lines.move_id = new_move
                new_move.push_routing_rule_id = rule
                move_lines.modified(["product_uom_qty"])
                assert move.state in ("assigned", "partially_available")
                # We know the new move is 'assigned' because we created it
                # with the quantity matching the move lines that we move into
                new_move.state = "assigned"
                new_moves += new_move

        return self + new_moves

    def _apply_routing_rule_push(self):
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
            routing_rule = move.push_routing_rule_id
            if not routing_rule:
                continue
            if move.picking_id.picking_type_id == routing_rule.picking_type_id:
                # already correct
                continue

            if self.env["stock.location"].search(
                [
                    ("id", "=", routing_rule.location_src_id.id),
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
            move.write({"location_dest_id": routing_rule.location_src_id.id})
            move.move_line_ids.write(
                {"location_dest_id": routing_rule.location_src_id.id}
            )

            move._insert_routing_moves(
                routing_rule.picking_type_id, routing_rule.location_src_id, destination
            )
