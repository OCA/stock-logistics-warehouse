# Copyright 2019 Camptocamp SA
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval

PENDING_MOVE_DOMAIN = [
    ("state", "in", ("waiting", "confirmed", "partially_available", "assigned"))
]


class StockLocation(models.Model):

    _inherit = "stock.location"

    pending_in_move_ids = fields.One2many(
        "stock.move",
        "location_dest_id",
        domain=PENDING_MOVE_DOMAIN,
        help="Technical field: the pending incoming stock moves for the location",
    )

    pending_in_move_line_ids = fields.One2many(
        "stock.move.line",
        "location_dest_id",
        domain=PENDING_MOVE_DOMAIN,
        help="Technical field: the pending incoming "
        "stock move lines for the location",
    )
    pending_out_move_ids = fields.One2many(
        "stock.move",
        "location_id",
        domain=PENDING_MOVE_DOMAIN,
        help="Technical field: the pending outgoing stock moves for the location",
    )
    pending_out_move_line_ids = fields.One2many(
        "stock.move.line",
        "location_id",
        domain=PENDING_MOVE_DOMAIN,
        help="Technical field: the pending outgoing "
        "stock move lines for the location",
    )

    def action_show_pending_stock_move_lines(self):
        """
        Display all pending stock move lines (outgoing and incoming)
        for the location.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.stock_move_line_action"
        )
        # Remove default searches from stock module
        context = action.get("context", "{}")
        context_dict = safe_eval(context)
        if "search_default_done" in context_dict:
            context_dict.pop("search_default_done")
        context_dict["search_default_todo"] = "1"
        context_dict["search_default_by_location"] = True
        action["context"] = str(context_dict)
        action.update(
            {
                "domain": [
                    (
                        "id",
                        "in",
                        (self.pending_out_move_line_ids | self.pending_in_move_line_ids)
                        .sorted()
                        .ids,
                    )
                ],
            }
        )
        return action

    def action_show_pending_stock_moves(self):
        """
        Display all pending stock moves (outgoing and incoming)
        for the location.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.stock_move_action"
        )
        # Remove default searches from stock module
        context = action.get("context", "{}")
        context_dict = safe_eval(context)
        if "search_default_done" in context_dict:
            context_dict.pop("search_default_done")
        context_dict["search_default_todo"] = "1"
        context_dict["search_default_groupby_location_id"] = True
        action["context"] = str(context_dict)
        action.update(
            {
                "domain": [
                    (
                        "id",
                        "in",
                        (self.pending_in_move_ids | self.pending_out_move_ids)
                        .sorted()
                        .ids,
                    )
                ],
            }
        )
        return action
