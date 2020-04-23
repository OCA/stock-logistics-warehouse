# Copyright (c) 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    direction = fields.Selection([('outbound', 'Outbound'),
                                  ('inbound', 'Inbound')],
                                 string='Direction',
                                 states={'draft': [('readonly', False)]},
                                 readonly=True)

    @api.onchange('warehouse_id', 'direction')
    def _onchange_location_id(self):
        if self.direction == 'outbound':
            # Stock Location set to Partner Locations/Customers
            self.location_id = \
                self.company_id.partner_id.property_stock_customer.id
        else:
            # Otherwise the Stock Location of the Warehouse
            self.location_id = \
                self.warehouse_id.lot_stock_id.id
        for stock_request in self.stock_request_ids:
            if stock_request.route_id:
                stock_request.route_id = False

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        # Onchange no longer needed
        pass

    def change_childs(self):
        super().change_childs()
        if not self._context.get('no_change_childs', False):
            for line in self.stock_request_ids:
                line.direction = self.direction
