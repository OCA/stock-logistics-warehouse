# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        if 'stock_request_id' in values and values.get('stock_request_id'):
            req = self.env['stock.request'].browse(
                values.get('stock_request_id'))
            if req.order_id:
                origin = req.order_id.name
        return super().run(product_id, product_qty, product_uom, location_id,
                           name, origin, values)
