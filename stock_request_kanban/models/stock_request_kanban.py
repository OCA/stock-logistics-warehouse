# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from reportlab.graphics.barcode import getCodes


class StockRequestKanban(models.Model):
    _name = 'stock.request.kanban'
    _description = 'Stock Request Kanban'
    _inherit = 'stock.request.abstract'

    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.request.kanban')
        return super().create(vals)

    @api.model
    def get_barcode_format(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'stock_request_kanban.barcode_format', default='Standard39'
        )

    @api.model
    def _recompute_barcode(self, barcode):
        if self.env['ir.config_parameter'].sudo().get_param(
            'stock_request_kanban.crc', default='1'
        ) == '0':
            return barcode
        bcc = getCodes()[self.get_barcode_format()](value=barcode[:-1])
        bcc.validate()
        bcc.encode()
        if bcc.encoded[1:-1] != barcode:
            raise ValidationError(_('CRC is not valid'))
        return barcode[:-1]

    @api.model
    def search_barcode(self, barcode):
        recomputed_barcode = self._recompute_barcode(barcode)
        return self.env['stock.request.kanban'].search([
            ('name', '=', recomputed_barcode)
        ])
