# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models, tools


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    display_completion_info = fields.Boolean(
        help="Inform operator of a completed operation at processing and at"
        " completion"
    )

    @api.model
    @tools.ormcache()
    def _completion_info_type_ids(self):
        """The operation types that show the completion information.

        Archived operation types count as well: their transfers still compute
        the field, and archiving does not go through the flag write below.
        """
        return tuple(
            self.sudo()
            .with_context(active_test=False)
            .search([("display_completion_info", "=", True)])
            .ids
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any(vals.get("display_completion_info") for vals in vals_list):
            self.env.registry.clear_cache()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "display_completion_info" in vals:
            self.env.registry.clear_cache()
        return res

    def unlink(self):
        flagged = any(self.mapped("display_completion_info"))
        res = super().unlink()
        if flagged:
            self.env.registry.clear_cache()
        return res


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
        "move_ids.common_dest_move_ids.state",
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
            depending_moves = picking.move_ids.mapped("common_dest_move_ids")
            # If all the depending moves are done or canceled then next picking
            # is ready to be processed
            if picking.state == "done" and all(
                m.state in ("done", "cancel") for m in depending_moves
            ):
                picking.completion_info = "next_picking_ready"
                continue
            # If all the depending moves are the moves on the actual picking
            # then it's a full order and next picking is ready to be processed
            if depending_moves == picking.move_ids:
                picking.completion_info = "full_order_picking"
                continue
            # If there aren't any depending move from another picking that is
            # not done, then actual picking is the last to process
            other_depending_moves = (depending_moves - picking.move_ids).filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            if not other_depending_moves:
                picking.completion_info = "last_picking"
                continue
            picking.completion_info = "no"


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            self._invalidate_completion_info()
        return res

    def _invalidate_completion_info(self):
        """Drop the completion information of the transfers this move reaches.

        The api.depends cannot express the conditions under which the field
        changes, so it has to be invalidated by hand. Doing that for the whole
        stock.picking model also flushes every pending write on it, once per
        move, which a transfer of a few hundred moves pays in full.

        Only two things can make the field anything other than "no": the
        transfer's own operation type shows the information, and the state of a
        move that shares a destination with one of its own has changed. So the
        transfers to invalidate are the one holding this move and the ones
        holding the moves around it, kept to those whose operation type shows
        the information at all.
        """
        type_ids = self.env["stock.picking.type"]._completion_info_type_ids()
        if not type_ids:
            # Nothing shows the information, so the field is "no" everywhere
            # and there is nothing cached that could have gone stale.
            return
        pickings = self.picking_id | self.common_dest_move_ids.picking_id
        stale = pickings.filtered(lambda p: p.picking_type_id.id in type_ids)
        if stale:
            stale.invalidate_recordset(fnames=["completion_info"])
