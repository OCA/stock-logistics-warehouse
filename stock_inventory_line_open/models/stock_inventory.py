# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_validated_inventory_lines(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "views": [
                (
                    self.env.ref(
                        "stock_inventory_line_open.stock_inventory_line_tree_readonly"
                    ).id,
                    "tree",
                )
            ],
            "view_mode": "tree",
            "name": _("Inventory Lines"),
            "res_model": "stock.inventory.line",
        }
        domain = [
            ("inventory_id", "=", self.id),
            ("location_id.usage", "in", ["internal", "transit"]),
        ]
        action["domain"] = domain
        return action
