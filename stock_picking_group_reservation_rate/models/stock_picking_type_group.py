# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools.safe_eval import safe_eval


class StockPickingTypeGroup(models.Model):
    _inherit = "stock.picking.type.group"

    def action_recompute_type_group_reservation_rate(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_picking_group_reservation_rate.recompute_reservation_rate_action"
        )
        context = safe_eval(action.get("context"), dict())
        context.update({"default_group_id": self.id})
        action["context"] = str(context)
        return action

    def _recompute_type_group_reservation_rate(self):
        """
        Recompute all moves in the selected group and
        that are not draft, cancelled or done.
        """
        Move = self.env["stock.move"]
        for group in self:
            moves = Move.search(
                [
                    ("state", "not in", ["draft", "cancel", "done"]),
                    ("picking_type_id.picking_type_group_id", "=", group.id),
                ]
            )
            moves._compute_type_group_reservation_rate()
