# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict
from functools import lru_cache

from odoo import fields, models


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
        comodel_name="stock.location",
        required=True,
        unique=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=lambda self: self._default_sequence())
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many(
        comodel_name="stock.routing.rule", inverse_name="routing_id"
    )

    _sql_constraints = [
        (
            "location_id_uniq",
            "unique(location_id)",
            "A routing configuration already exists for this location",
        )
    ]

    def _default_sequence(self):
        return _default_sequence(self)

    # TODO would be nice to add a constraint that would prevent to
    # have a pull + a pull routing that would apply on the same move
    # TODO write tests for this
    def _find_rule_for_location(self, move, src_location, dest_location):
        """Return the routing rule for a source or destination location

        It searches first a routing pull rule based on the source location,
        and if nothing is found, it searches for a routing push rule based
        on the destination location.

        The source/destination locations are not an exact match: it looks
        for the location or a parent.
        """
        # the result of _location_parent_tree() is cached, so get the rules
        # at once even if we don't use the "push" candidates, we can spare
        # some queries
        pull_location_tree = src_location._location_parent_tree()
        push_location_tree = dest_location._location_parent_tree()
        candidate_rules = self.env["stock.routing.rule"].search(
            [
                "|",
                "&",
                ("routing_location_id", "in", pull_location_tree.ids),
                ("method", "=", "pull"),
                "&",
                ("routing_location_id", "in", push_location_tree.ids),
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
