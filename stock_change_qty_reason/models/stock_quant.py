# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    reason = fields.Char(help="Type in a reason for the product quantity change")
    preset_reason_id = fields.Many2one(
        comodel_name="stock.inventory.reason", string="Preset Reason"
    )

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        result = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out=out
        )
        extra_origin = (
            self.reason if not self.preset_reason_id else self.preset_reason_id.name
        )
        if result.get("origin", False):
            result["origin"] = " ,".join([result.get("origin"), extra_origin])
        else:
            result["origin"] = extra_origin
        return result

    @api.model
    def _get_inventory_fields_write(self):
        result = super()._get_inventory_fields_write()
        new_fields = ["reason", "preset_reason_id"]
        return result + new_fields
