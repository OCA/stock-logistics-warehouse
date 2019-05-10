# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'stock_request'),
            ('warehouse_id.company_id', 'in',
             [self.env.context.get('company_id', self.env.user.company_id.id),
              False])],
            limit=1).id

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type, required=True)
