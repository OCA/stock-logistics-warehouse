# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class PickingType(models.Model):

    _inherit = "stock.picking.type"

    display_completion_info = fields.Boolean(
        help="Inform operator of a completed operation at processing and at"
        " completion"
    )


class StockPicking(models.Model):

    _inherit = "stock.picking"

    completion_info = fields.Selection(
        [
            ("no", "No"),
            (
                "last_picking",
                "Last picking: Completion of this operation allows next "
                "operations to be processed.",
            ),
            ("next_picking_ready", "Next operations are ready to be processed."),
            (
                "full_order_picking",
                "Full order picking: You are processing a full order picking "
                "that will allow next operation to be processed",
            ),
        ],
        compute="_compute_completion_info",
    )

    @api.depends(
        "picking_type_id.display_completion_info",
        "move_lines.common_dest_move_ids.state",
    )
    def _compute_completion_info(self):
        for picking in self:
            if (
                picking.state == "draft"
                or not picking.picking_type_id.display_completion_info
            ):
                picking.completion_info = "no"
                continue
            # Depending moves are all the origin moves linked to the
            # destination pickings' moves
            depending_moves = picking.move_lines.mapped("common_dest_move_ids")
            # If all the depending moves are done or canceled then next picking
            # is ready to be processed
            if picking.state == "done" and all(
                m.state in ("done", "cancel") for m in depending_moves
            ):
                picking.completion_info = "next_picking_ready"
                continue
            # If all the depending moves are the moves on the actual picking
            # then it's a full order and next picking is ready to be processed
            if depending_moves == picking.move_lines:
                picking.completion_info = "full_order_picking"
                continue
            # If there aren't any depending move from another picking that is
            # not done, then actual picking is the last to process
            other_depending_moves = (depending_moves - picking.move_lines).filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            if not other_depending_moves:
                picking.completion_info = "last_picking"
                continue
            picking.completion_info = "no"


class StockMove(models.Model):

    _inherit = "stock.move"

    def write(self, vals):
        super().write(vals)
        if "state" in vals:
            # invalidate cache, the api.depends do not allow to find all
            # the conditions to invalidate the field
            self.env["stock.picking"].invalidate_cache(fnames=["completion_info"])
        return True
