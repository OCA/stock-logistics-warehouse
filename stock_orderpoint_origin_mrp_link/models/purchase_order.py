# Copyright 2021 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends(
        "order_line.move_dest_ids.group_id.mrp_production_ids",
        "order_line.source_group_ids",
    )
    def _compute_mrp_production_count(self):
        super()._compute_mrp_production_count()
        for purchase in self:
            mos_to_add = purchase.order_line.source_group_ids.mrp_production_ids
            purchase.mrp_production_count += len(mos_to_add)

    def action_view_mrp_productions(self):
        action = super().action_view_mrp_productions()
        mos_to_add = self.order_line.source_group_ids.mrp_production_ids
        if mos_to_add:
            if self.mrp_production_count == 1:
                action = {
                    "res_model": "mrp.production",
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_id": mos_to_add.id,
                }
            else:
                old_domain = action.get("domain") or [("id", "=", action.get("res_id"))]
                new_domain = ["|", ("id", "in", mos_to_add.ids)] + old_domain
                action = {
                    "res_model": "mrp.production",
                    "type": "ir.actions.act_window",
                    "name": _("Manufacturing Source of %s", self.name),
                    "domain": new_domain,
                    "view_mode": "tree,form",
                }
        return action
