# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    dest_picking_count = fields.Integer(compute="_compute_picking_count")
    origin_picking_count = fields.Integer(compute="_compute_picking_count")

    @api.depends("move_lines")
    def _compute_picking_count(self):
        for record in self:
            origin_pickings = record.mapped("move_lines.move_orig_ids.picking_id")
            dest_pickings = record.mapped("move_lines.move_dest_ids.picking_id")
            record.origin_picking_count = len(origin_pickings)
            record.dest_picking_count = len(dest_pickings)

    def _get_action_link(self, pickings):
        result = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # choose the view_mode accordingly
        if not pickings or len(pickings) > 1:
            result["domain"] = "[('id','in',%s)]" % pickings
        elif len(pickings) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = pickings[0]
        return result

    def action_stock_picking_origin(self):
        pick_ids = self.mapped("move_lines.move_orig_ids.picking_id")
        result = self._get_action_link(pick_ids.ids)
        return result

    def action_stock_picking_destination(self):
        pick_ids = self.mapped("move_lines.move_dest_ids.picking_id")
        result = self._get_action_link(pick_ids.ids)
        return result
