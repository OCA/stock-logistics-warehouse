# Copyright 2022 ForgeFlow <http://www.forgeflow.com>

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.move.line"

    def action_view_mrp_from_reserved(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_production_action"
        )
        action["views"] = [(self.env.ref("mrp.mrp_production_form_view").id, "form")]
        action["res_id"] = self.production_id.id
        return action
