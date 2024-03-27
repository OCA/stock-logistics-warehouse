# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression


class StockMove(models.Model):

    _inherit = "stock.move"

    reservation_date = fields.Date(
        "Date to Reserve",
        compute="_compute_reservation_date",
        store=True,
        help="This is a technical field for "
        "calculating when a move should be reserved",
    )

    @api.depends("picking_type_id", "date", "priority", "state")
    def _compute_reservation_date(self):
        for move in self:
            if move.picking_type_id.reservation_method == "by_date" and move.state in [
                "draft",
                "confirmed",
                "waiting",
                "partially_available",
            ]:
                days = move.picking_type_id.reservation_days_before
                if move.priority == "1":
                    days = move.picking_type_id.reservation_days_before_priority
                move.reservation_date = fields.Date.to_date(move.date) - timedelta(
                    days=days
                )

    # Override
    def _trigger_assign(self):
        if not self or self.env["ir.config_parameter"].sudo().get_param(
            "stock.picking_no_auto_reserve"
        ):
            return
        domains = []
        for move in self:
            domains.append(
                [
                    ("product_id", "=", move.product_id.id),
                    ("location_id", "=", move.location_dest_id.id),
                ]
            )
        static_domain = [
            ("state", "in", ["confirmed", "partially_available"]),
            ("procure_method", "=", "make_to_stock"),
            ("reservation_date", "<=", fields.Date.today()),
        ]
        moves_to_reserve = self.env["stock.move"].search(
            expression.AND([static_domain, expression.OR(domains)]),
            order="reservation_date, priority desc, date asc, id asc",
        )
        moves_to_reserve._action_assign()
