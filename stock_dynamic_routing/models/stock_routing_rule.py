# Copyright 2019-2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, exceptions, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from .stock_routing import _default_sequence


class StockRoutingRule(models.Model):
    _name = "stock.routing.rule"
    _description = "Stock Dynamic Routing Rule"
    _order = "sequence, id"

    sequence = fields.Integer(default=lambda self: self._default_sequence())
    routing_id = fields.Many2one(
        comodel_name="stock.routing", required=True, ondelete="cascade"
    )
    routing_location_id = fields.Many2one(
        related="routing_id.location_id", store=True, index=True
    )
    routing_picking_type_id = fields.Many2one(
        related="routing_id.picking_type_id",
        store=True,
        index=True,
        help="Routing applied only on moves of this operation type.",
    )
    method = fields.Selection(
        selection=[("pull", "Pull"), ("push", "Push")],
        help="On pull, the routing is applied when the source location of "
        "a move line matches the source location of the rule. "
        "On push, the routing is applied when the destination location of "
        "a move line matches the destination location of the rule.",
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        required=True,
        help="Operation type that will be applied on the move.",
    )
    location_src_id = fields.Many2one(
        related="picking_type_id.default_location_src_id", readonly=True
    )
    location_dest_id = fields.Many2one(
        related="picking_type_id.default_location_dest_id", readonly=True
    )
    rule_domain = fields.Char(
        string="Source Routing Domain",
        default=[],
        help="Domain based on Stock Moves, to define if the "
        "routing rule is applicable or not.",
    )

    def _default_sequence(self):
        return _default_sequence(self)

    @api.constrains("picking_type_id")
    def _constrains_picking_type_location(self):
        for record in self:
            base_location = record.routing_location_id

            if record.method == "pull" and (
                not record.location_src_id
                or not record.location_src_id.is_sublocation_of(base_location)
            ):
                raise exceptions.ValidationError(
                    _(
                        "Operation type of a rule used as 'pull' must have '{}'"
                        " or a sub-location as source location."
                    ).format(base_location.display_name)
                )
            elif record.method == "push" and (
                not record.location_dest_id
                or not record.location_dest_id.is_sublocation_of(base_location)
            ):

                raise exceptions.ValidationError(
                    _(
                        "Operation type of a rule used as 'push' must have '{}'"
                        " or a sub-location as destination location."
                    ).format(base_location.display_name)
                )

    def _is_valid_for_moves(self, moves):
        if not self.rule_domain:
            return self
        domain = safe_eval(self.rule_domain)
        return self._eval_routing_domain(moves, domain)

    def _eval_routing_domain(self, moves, domain):
        if not domain:
            return self
        move_domain = [("id", "in", moves.ids)]
        # Warning: if we build a domain with dotted path such as
        # group_id.is_urgent (hypothetic field), can become very slow as odoo
        # searches all "procurement.group.is_urgent" first then uses "IN
        # group_ids" on the stock move only. In such situations, it can be
        # better either to add a related field on the stock.move, either extend
        # _is_valid_for_moves to add your own logic (based on SQL, ...).
        return self.env["stock.move"].search(expression.AND([move_domain, domain]))
