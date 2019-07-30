# Copyright (c) 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    direction = fields.Selection([('outbound', 'Outbound'),
                                  ('inbound', 'Inbound')],
                                 string='Direction',
                                 states={'draft': [('readonly', False)]},
                                 readonly=True)

    @api.onchange('direction')
    def _onchange_location_id(self):
        if self.direction == 'outbound':
            # Partner Locations/Customers
            self.location_id = self.env.ref('stock.stock_location_customers')
        else:
            # Otherwise the Stock Location of the Warehouse
            self.location_id = self.warehouse_id.lot_stock_id.id
