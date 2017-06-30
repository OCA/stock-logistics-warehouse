# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _prepare_orderpoint_vals(self, warehouse):
        company = self.env.user.company_id
        return {
            'name': self.name,
            'product_id': self.id,
            'product_max_qty': company.orderpoint_product_max_qty,
            'product_min_qty': company.orderpoint_product_min_qty,
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id
        }

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        if not product.type == 'product' or product.create_orderpoint == 'no':
            return product
        if product.create_orderpoint == 'yes' \
            or product.categ_id.create_orderpoints == 'yes' \
                or self.env.user.company_id.create_orderpoints:
            orderpoint_obj = self.env['stock.warehouse.orderpoint']
            wh_obj = self.env['stock.warehouse']
            warehouses = wh_obj.search([
                ('company_id', '=', self.env.user.company_id.id),
            ])
            for warehouse in warehouses:
                values = product._prepare_orderpoint_vals(warehouse)
                orderpoint_obj.create(values)
        return product
