# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo import api, fields, models


# class StockRoute(models.Model):
#     _inherit = "stock.route"

#     is_location_blocked = fields.Boolean(
#         compute="_compute_is_location_blocked",
#         store=True,
#         help="True if any of the route's rules has a blocked source or "
#         "destination location. Use this for route selection filtering.",
#     )

#     @api.model
#     def _is_location_blocked_depends(self):
#         return ("rule_ids.is_location_blocked",)

#     @api.depends(lambda self: self._is_location_blocked_depends())
#     def _compute_is_location_blocked(self):
#         for route in self:
#             route.is_location_blocked = any(
#                 rule.is_location_blocked for rule in route.rule_ids
#             )
