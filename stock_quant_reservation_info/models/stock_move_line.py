# Copyright 2022 ForgeFlow <http://www.forgeflow.com>

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.move.line"

    def action_view_picking_from_reserved(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        res = self.env.ref("stock.view_picking_form", False)
        action["views"] = [(res and res.id or False, "form")]
        action["res_id"] = self.picking_id.id
        return action
