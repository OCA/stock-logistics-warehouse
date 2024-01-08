# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    inventory_justification_ids = fields.Many2many(
        string="Justifications",
        help="Inventory justifications",
        comodel_name="stock.inventory.justification",
        relation="stock_quant_inventory_justification_rel",
        column1="quant_id",
        column2="justification_id",
    )

    def action_inventory_history(self):  # pragma: no cover
        action = super().action_inventory_history()
        action["context"]["show_inventory_justifications"] = True
        return action

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        res["inventory_justification_ids"] = [
            (6, 0, self.inventory_justification_ids.ids)
        ]
        return res

    def _apply_inventory(self):
        res = super()._apply_inventory()
        self.write({"inventory_justification_ids": [(5,)]})
        return res

    @api.model
    def _get_inventory_fields_write(self):
        res = super()._get_inventory_fields_write()
        res.append("inventory_justification_ids")
        return res
