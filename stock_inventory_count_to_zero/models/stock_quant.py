# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_set_inventory_quantity_recount_to_zero(self):
        quants_already_set = self.filtered(lambda quant: quant.inventory_quantity_set)
        if quants_already_set:
            ctx = dict(self.env.context or {}, default_quant_ids=self.ids)
            view = self.env.ref("stock.inventory_warning_set_view", False)
            return {
                "name": _("Quantities Already Set"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(view.id, "form")],
                "view_id": view.id,
                "res_model": "stock.inventory.warning",
                "target": "new",
                "context": ctx,
            }
        self.update(
            {
                "inventory_quantity": 0.0,
                "user_id": self.env.user.id,
                "inventory_quantity_set": True,
            }
        )
