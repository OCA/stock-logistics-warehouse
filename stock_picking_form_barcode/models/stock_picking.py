# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from base64 import b64encode

from odoo import api, fields, models
from odoo.fields import NewId


class StockPicking(models.Model):
    _inherit = "stock.picking"

    barcode_visible = fields.Boolean(related="picking_type_id.display_picking_barcode")
    barcode = fields.Image(compute="_compute_barcode")

    @api.depends("name")
    def _compute_barcode(self):
        for picking in self:
            if picking.name == "/" or isinstance(picking.id, NewId):
                picking.barcode = False
            else:
                barcode_input = self.env["ir.actions.report"].barcode(
                    barcode_type="auto", value=picking.name, humanreadable=False
                )
                picking.barcode = b64encode(barcode_input)
