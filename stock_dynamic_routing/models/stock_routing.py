# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict
from functools import lru_cache

from odoo import _, api, fields, models


def _default_sequence(model):
    maxrule = model.search([], order="sequence desc", limit=1)
    if maxrule:
        return maxrule.sequence + 10
    else:
        return 0


class StockRouting(models.Model):
    _name = "stock.routing"
    _description = "Stock Dynamic Routing"
    _order = "sequence, id"

    _rec_name = "location_id"

    location_id = fields.Many2one(
        comodel_name="stock.location", required=True, ondelete="cascade", index=True,
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        required=True,
        help="Apply this routing only if the operation type of the move is the same.",
    )
    sequence = fields.Integer(default=lambda self: self._default_sequence())
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many(
        comodel_name="stock.routing.rule", inverse_name="routing_id"
    )
    routing_message = fields.Html(compute="_compute_routing_message")

    _sql_constraints = [
        (
            "location_picking_type_uniq",
            "unique(location_id, picking_type_id)",
            "A routing configuration already exists for this location and picking type",
        )
    ]

    def _routing_message_template(self):
        pull_rules = self.rule_ids.filtered(lambda r: r.method == "pull")
        push_rules = self.rule_ids.filtered(lambda r: r.method == "push")
        pull_message = ""
        push_message = ""

        if pull_rules:
            rule_messages = []
            for rule in pull_rules:
                msg = _(
                    "If the destination of the move is already"
                    " <strong>{rule.location_dest_id.display_name}</strong>,"
                    " the operation type of the move is changed to"
                    " <strong>{rule.picking_type_id.display_name}</strong>."
                    "<br/>"
                    "If the destination of the move is a parent location of "
                    " <strong>{rule.location_dest_id.display_name}</strong>,"
                    " the destination is set to "
                    "<strong>{rule.location_dest_id.display_name}</strong> "
                    " and the operation type of the move is changed to"
                    " <strong>{rule.picking_type_id.display_name}</strong>."
                    "<br/>"
                    "If the destination of the move is unrelated to "
                    " <strong>{rule.location_dest_id.display_name}</strong>, "
                    "a new move is added before, from"
                    " <strong>{rule.location_src_id.display_name}</strong> to "
                    " <strong>{rule.location_dest_id.display_name}</strong>, "
                    "using the operation type "
                    " <strong>{rule.picking_type_id.display_name}</strong>."
                ).format(rule=rule)
                rule_messages.append("<li>" + msg + "</li>")
            pull_message = _(
                "<h2>Pull rules:</h2>"
                "When a move with operation type "
                "<strong>{routing.picking_type_id.display_name}</strong>"
                " has a source location"
                " <strong>{routing.location_id.display_name}</strong>"
                " (or a sub-location), one of these rules can apply (depending"
                " of their domain):"
                "<ul>"
                "{rule_messages}"
                "</ul>"
            ).format(routing=self, rule_messages="\n".join(rule_messages))

        if push_rules:
            rule_messages = []
            for rule in push_rules:
                msg = _(
                    "If the source of the move is already"
                    " <strong>{rule.location_src_id.display_name}</strong>"
                    " or a sub-location, the operation type of the move"
                    " is changed to"
                    " <strong>{rule.picking_type_id.display_name}</strong>."
                    "<br/>"
                    "If the source of the move is outside or a parent location of "
                    " <strong>{rule.location_dest_id.display_name}</strong>,"
                    " the destination of the move is set to "
                    " <strong>{rule.location_src_id.display_name}</strong>, "
                    " a new move is added after it, from"
                    " <strong>{rule.location_src_id.display_name}</strong> to "
                    " <strong>{rule.location_dest_id.display_name}</strong> "
                    "using the operation type "
                    " <strong>{rule.picking_type_id.display_name}</strong>."
                ).format(rule=rule)
                rule_messages.append("<li>" + msg + "</li>")
            push_message = _(
                "<h2>Push rules:</h2>"
                "When a move with operation type "
                "<strong>{routing.picking_type_id.display_name}</strong>"
                " has a destination location"
                " <strong>{routing.location_id.display_name}</strong>"
                " (or a sub-location), one of these rules can apply (depending"
                " of their domain):"
                "<ul>"
                "{rule_messages}"
                "</ul>"
            ).format(routing=self, rule_messages="\n".join(rule_messages))
        return pull_message + "<br/>" + push_message

    @api.depends(
        "location_id", "picking_type_id", "rule_ids.method", "rule_ids.picking_type_id"
    )
    def _compute_routing_message(self):
        """Generate a description of the routing for humans"""
        for routing in self:
            if not (
                routing.picking_type_id and routing.location_id and routing.rule_ids
            ):
                routing.routing_message = ""
                continue
            routing.routing_message = routing._routing_message_template().format(
                routing=routing
            )

    def _default_sequence(self):
        return _default_sequence(self)

    # TODO would be nice to add a constraint that would prevent to
    # have a pull + a push routing that would apply on the same move
    def _find_rule_for_location(self, move, src_location, dest_location):
        """Return the routing rule for a source or destination location

        It searches first a routing pull rule based on the source location,
        and if nothing is found, it searches for a routing push rule based
        on the destination location.

        The source/destination locations are not an exact match: it looks
        for the location or a parent.
        """
        pull_location_tree = src_location._location_parent_tree()
        push_location_tree = dest_location._location_parent_tree()
        picking_type = move.picking_type_id or move.picking_id.picking_type_id
        candidate_rules = self.env["stock.routing.rule"].search(
            [
                "|",
                "&",
                "&",
                ("routing_location_id", "in", pull_location_tree.ids),
                ("routing_picking_type_id", "=", picking_type.id),
                ("method", "=", "pull"),
                "&",
                "&",
                ("routing_location_id", "in", push_location_tree.ids),
                ("routing_picking_type_id", "=", picking_type.id),
                ("method", "=", "push"),
            ]
        )
        candidate_rules.sorted(lambda r: (r.routing_id.sequence, r.sequence))
        rule = self._get_location_routing_rule(
            move, pull_location_tree, candidate_rules
        )
        if rule:
            return rule

        rule = self._get_location_routing_rule(
            move, push_location_tree, candidate_rules
        )
        if rule:
            return rule

        empty_rule = self.env["stock.routing.rule"].browse()
        return empty_rule

    def _routing_rule_for_move_lines(self, moves):
        """Return a routing rule for move lines

        Look first for a pull routing rule, if no match, look for a push
        routing rule.

        :param move: recordset of the move
        :return: dict {move: {rule: move_lines}}
        """
        # ensure the cache is clean
        self.__cached_is_rule_valid_for_move.cache_clear()

        result = {
            move: defaultdict(self.env["stock.move.line"].browse) for move in moves
        }
        for move_line in moves.mapped("move_line_ids"):
            rule = self._find_rule_for_location(
                move_line.move_id, move_line.location_id, move_line.location_dest_id
            )
            result[move_line.move_id][rule] |= move_line

        # free memory used for the cache
        self.__cached_is_rule_valid_for_move.cache_clear()
        return result

    def _routing_rule_for_moves(self, moves):
        """Return a routing rule for moves

        Look first for a pull routing rule, if no match, look for a push
        routing rule.

        :param move: recordset of the move
        :return: dict {move: rule}}
        """
        # ensure the cache is clean
        self.__cached_is_rule_valid_for_move.cache_clear()

        result = {}
        for move in moves:
            rule = self._find_rule_for_location(
                move, move.location_id, move.location_dest_id
            )
            result[move] = rule

        # free memory used for the cache
        self.__cached_is_rule_valid_for_move.cache_clear()
        return result

    # Do not use ormcache, which would invalidate cache of other workers every
    # time we clear it. We only need a local cache used for the duration of the
    # execution of
    @lru_cache()
    def __cached_is_rule_valid_for_move(self, rule, move):
        """To be used only by _routing_rule_for_move(_line)s

        The method _routing_rule_for_move(_line)s reset the cache at beginning.
        Cache the result so inside _routing_rule_for_move(_line)s, we compute it
        only once for a move and a rule (if we have several move lines).
        """
        return rule._is_valid_for_moves(move)

    def _get_location_routing_rule(self, move, location_tree, rules):
        # the first location is the current move line's source or dest
        # location, then we climb up the tree of locations
        for loc in location_tree:
            # find the first valid rule
            for rule in rules.filtered(lambda r: r.routing_location_id == loc):
                if not self.__cached_is_rule_valid_for_move(rule, move):
                    continue
                return rule
        return self.env["stock.routing.rule"].browse()
