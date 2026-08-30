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
            # defaults
            width = 600
            height = 100
            if picking.name == "/" or isinstance(picking.id, NewId):
                picking.barcode = False
            else:
                code_format = picking.picking_type_id.picking_barcode_format
                if not code_format:
                    code_format = "auto"
                if code_format == "QR":
                    width = 100
                barcode_input = self.env["ir.actions.report"].barcode(
                    barcode_type=code_format,
                    value=picking.name,
                    width=width,
                    height=height,
                    humanreadable=False,
                )
                picking.barcode = b64encode(barcode_input)
