# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    dest_picking_ids = fields.Many2many(
        comodel_name="stock.picking", compute="_compute_dest_picking"
    )

    dest_picking_count = fields.Integer(compute="_compute_dest_picking")

    @api.depends(
        "move_ids_without_package.move_dest_ids.picking_id",
        "move_ids_without_package",
        "move_ids_without_package.move_dest_ids",
    )
    def _compute_dest_picking(self):
        for rec in self:
            rec.dest_picking_ids = rec.move_ids_without_package.move_dest_ids.mapped(
                "picking_id"
            )
            rec.dest_picking_count = len(rec.dest_picking_ids)

    def action_view_dest_picking_ids(self):
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        if not self.dest_picking_ids or len(self.dest_picking_ids) > 1:
            result["domain"] = "[('id','in',%s)]" % (self.dest_picking_ids.ids)
        elif len(self.dest_picking_ids) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = self.dest_picking_ids.id
        return result
