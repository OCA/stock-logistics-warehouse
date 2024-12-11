# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    origin_picking_count = fields.Integer(compute="_compute_picking_count")

    @api.depends("move_ids.move_orig_ids")
    def _compute_picking_count(self):
        for record in self:
            origin_pickings = record.mapped("move_ids.move_orig_ids.picking_id")
            record.update(
                {
                    "origin_picking_count": len(origin_pickings),
                }
            )

    def _get_action_link(self, picking_ids):
        result = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # choose the view_mode accordingly
        if not picking_ids or len(picking_ids) > 1:
            result["domain"] = f"[('id','in',{picking_ids})]"
        elif len(picking_ids) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = picking_ids[0]
        return result

    def action_stock_picking_origin(self):
        pick_ids = self.mapped("move_ids.move_orig_ids.picking_id")
        result = self._get_action_link(pick_ids.ids)
        return result
