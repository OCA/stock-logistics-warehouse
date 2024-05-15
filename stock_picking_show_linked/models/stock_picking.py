# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    dest_picking_count = fields.Integer(compute="_compute_picking_count")
    origin_picking_count = fields.Integer(compute="_compute_picking_count")

    @api.depends("move_ids")
    def _compute_picking_count(self):
        for record in self:
            # Exclude the return as V17 already have return smart button.
            origin_pickings = record.mapped("move_ids.move_orig_ids.picking_id") - record.return_ids
            dest_pickings = record.mapped("move_ids.move_dest_ids.picking_id") - record.return_ids
            record.origin_picking_count = len(origin_pickings)
            record.dest_picking_count = len(dest_pickings)

    def _get_action_link(self, pickings):
        self.ensure_one()
        from_view_id = self.env.ref("stock.view_picking_form", False)
        list_view_id = self.env.ref("stock.vpicktree", False)

        if len(pickings) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "view_id": from_view_id,
                "views": [[False, "form"]],
                "res_id": pickings[0]
            }
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "name": "Transfers",
            "view_id": list_view_id,
            "views": [[False, "tree"], [False, "form"]],
            "domain": [('id', 'in', pickings)],
        }

    def action_stock_picking_origin(self):
        pick_ids = self.mapped("move_ids.move_orig_ids.picking_id") - self.return_ids  # Exclude the return as V17 already have return smart button
        result = self._get_action_link(pick_ids.ids)
        return result

    def action_stock_picking_destination(self):
        pick_ids = self.mapped("move_ids.move_dest_ids.picking_id") - self.return_ids  # Exclude the return as V17 already have return smart button
        result = self._get_action_link(pick_ids.ids)
        return result
