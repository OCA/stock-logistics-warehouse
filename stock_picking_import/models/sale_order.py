# © 2021 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_partial_wizard(self):
        self.ensure_one()

        view = self.env.ref("stock_picking_import.view_partial_picking_wizard")

        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "stock.partial.picking",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": {
                "default_order_id": self.id,
            },
        }
