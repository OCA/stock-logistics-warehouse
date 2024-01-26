# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _trigger_scheduler(self):
        if not self or self.env["ir.config_parameter"].sudo().get_param(
            "stock.no_auto_scheduler"
        ):
            return

        for move in self:
            orderpoint = self.env["stock.warehouse.orderpoint"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("trigger", "=", "auto"),
                    ("location_id", "parent_of", move.location_id.id),
                    ("company_id", "=", move.company_id.id),
                ],
                limit=1,
            )
            if not orderpoint:
                template = self.env["stock.warehouse.orderpoint.template"].search(
                    [
                        ("location_id", "parent_of", move.location_id.id),
                        ("company_id", "=", move.company_id.id),
                    ],
                    limit=1,
                )
                if template:
                    template._create_orderpoint(move.product_id)
        return super()._trigger_scheduler()
