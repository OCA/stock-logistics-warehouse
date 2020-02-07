# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from reportlab.graphics.barcode import getCodes

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequestKanban(models.Model):
    _name = "stock.request.kanban"
    _description = "Stock Request Kanban"
    _inherit = "stock.request.abstract"

    active = fields.Boolean(default=True)
    product_template_id = fields.Many2one(related="product_id.product_tmpl_id")

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = self.env["ir.sequence"].next_by_code("stock.request.kanban")
        return super().create(vals)

    @api.model
    def get_barcode_format(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_request_kanban.barcode_format", default="Standard39")
        )

    @api.model
    def _recompute_barcode(self, barcode):
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_request_kanban.crc", default="1")
            == "0"
        ):
            return barcode
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_request_kanban.ignore_crc", default="0")
            == "0"
        ):
            bcc = getCodes()[self.get_barcode_format()](value=barcode[:-1])
            bcc.validate()
            bcc.encode()
            if bcc.encoded[1:-1] != barcode:
                raise ValidationError(_("CRC is not valid"))
        return barcode[:-1]

    @api.model
    def search_barcode(self, barcode):
        recomputed_barcode = self._recompute_barcode(barcode)
        return self.env["stock.request.kanban"].search(
            [("name", "ilike", recomputed_barcode)]
        )
