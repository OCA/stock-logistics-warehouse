# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import fields, models, tools


def _default_sequence(model):
    maxrule = model.search([], order="sequence desc", limit=1)
    if maxrule:
        return maxrule.sequence + 10
    else:
        return 0


class StockRouting(models.Model):
    _name = "stock.routing"
    _description = "Stock Routing"
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

    # TODO write tests for this
    # TODO would be nice to add a constraint that would prevent to
    # have a pull + a pull routing that would apply on the same move
    def _routing_rule_for_moves(self, moves):
        """Return a routing rule for moves

        Look first for a pull routing rule, if no match, look for a push
        routing rule.

        :param move: recordset of the move
        :return: dict {move: {rule: move_lines}}
        """
        self.__cached_is_rule_valid_for_move.clear_cache(self)
        result = {
            move: defaultdict(self.env["stock.move.line"].browse) for move in moves
        }
        empty_rule = self.env["stock.routing.rule"].browse()
        for move_line in moves.mapped("move_line_ids"):
            src_location = move_line.location_id
            dest_location = move_line.location_dest_id
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
            rule = self._get_move_line_routing_rule(
                move_line, pull_location_tree, candidate_rules
            )
            if rule:
                result[move_line.move_id][rule] |= move_line
                continue

            rule = self._get_move_line_routing_rule(
                move_line, push_location_tree, candidate_rules
            )
            if rule:
                result[move_line.move_id][rule] |= move_line
                continue

            result[move_line.move_id][empty_rule] |= move_line

        return result

    @tools.ormcache("rule", "move")
    def __cached_is_rule_valid_for_move(self, rule, move):
        """To be used only by _routing_rule_for_moves

        The method _routing_rule_for_moves reset the cache at beginning.
        Cache the result so inside _routing_rule_for_moves, we compute it
        only once for a move an a rule.
        """
        return rule._is_valid_for_moves(move)

    def _get_move_line_routing_rule(self, move_line, location_tree, rules):
        # the first location is the current move line's source or dest
        # location, then we climb up the tree of locations
        for loc in location_tree:
            # find the first valid rule
            for rule in rules.filtered(lambda r: r.routing_location_id == loc):
                if not self.__cached_is_rule_valid_for_move(rule, move_line.move_id):
                    continue
                return rule
        return self.env["stock.routing.rule"].browse()
