# -*- coding: utf-8 -*-
# (c) 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        result = super(ProductProduct, self).create(vals)
        orderpoint_obj = self.env['stock.warehouse.orderpoint']
        wh_obj = self.env['stock.warehouse']
        if result.type != 'service':
            if self.env.user.company_id.create_orderpoints:
                company = self.env.user.company_id
                warehouses = wh_obj.search([('company_id', '=', company.id)])
                for warehouse in warehouses:
                    orderpoint_obj.create(
                        {'name': result.name,
                         'product_id': result.id,
                         'product_max_qty': company.orderpoint_product_max_qty,
                         'product_min_qty': company.orderpoint_product_min_qty,
                         'warehouse_id': warehouse.id,
                         'location_id': warehouse.lot_stock_id.id,
                         })
        return result
