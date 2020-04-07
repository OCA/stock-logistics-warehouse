# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockRouting(models.Model):
    _name = "stock.routing"
    _description = "Stock Routing"
    _order = "location_id"

    _rec_name = "location_id"

    location_id = fields.Many2one(
        comodel_name="stock.location",
        required=True,
        unique=True,
        ondelete="cascade",
        index=True,
    )
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

    def _routing_rule_for_moves(self, method, moves):
        """Return a routing rule for moves

        :param method: pull (pick) or push (put-away)
        :param move: recordset of the move
        :return: dict {move: {rule: move_lines}}
        """
        if method not in ("pull", "push"):
            raise ValueError("routing_type must be one of ('pull', 'push')")

        result = {move: {} for move in moves}
        valid_rules_for_move = set()
        for move_line in moves.mapped("move_line_ids"):
            if method == "pull":
                location = move_line.location_id
            else:
                location = move_line.location_dest_id
            location_tree = location._location_parent_tree()
            candidate_routings = self.search([("location_id", "in", location_tree.ids)])

            result.setdefault(move_line.move_id, [])
            # the first location is the current move line's source or dest
            # location, then we climb up the tree of locations
            for loc in location_tree:
                # and search the first allowed rule in the routing
                routing = candidate_routings.filtered(lambda r: r.location_id == loc)
                rules = routing.rule_ids.filtered(lambda r: r.method == method)
                # find the first valid rule
                found = False
                for rule in rules:
                    if not (
                        (move_line.move_id, rule) in valid_rules_for_move
                        or rule._is_valid_for_moves(move_line.move_id)
                    ):
                        continue
                    # memorize the result so we don't compute it for
                    # every move line
                    valid_rules_for_move.add((move_line.move_id, rule))
                    if rule in result[move_line.move_id]:
                        result[move_line.move_id][rule] |= move_line
                    else:
                        result[move_line.move_id][rule] = move_line
                    found = True
                    break
                if found:
                    break
            else:
                empty_rule = self.env["stock.routing.rule"].browse()
                if empty_rule in result[move_line.move_id]:
                    result[move_line.move_id][empty_rule] |= move_line
                else:
                    result[move_line.move_id][empty_rule] = move_line
        return result
