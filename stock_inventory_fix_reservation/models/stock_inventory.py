# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class Inventory(models.Model):
    _inherit = "stock.inventory"

    def post_inventory(self):
        lines = self.line_ids.filtered(lambda l: l.difference_qty < 0)
        domain = [
            ("location_id", "in", lines.mapped("location_id").ids),
            ("product_id", "in", lines.mapped("product_id").ids),
            ("state", "in", ["assigned", "partially_available"]),
        ]
        assigned_moves = self.env["stock.move.line"].search(domain).mapped("move_id")
        result = super().post_inventory()
        assigned_moves._action_assign()
        return result
