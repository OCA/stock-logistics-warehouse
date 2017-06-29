# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        result = super(ProductProduct, self).create(vals)
        orderpoint_obj = self.env['stock.warehouse.orderpoint']
        wh_obj = self.env['stock.warehouse']
        create = False
        if not result.type == 'product' or result.create_orderpoint == 'no':
            return result
        elif result.create_orderpoint == 'yes':
            create = True
        elif result.categ_id.create_orderpoints == 'no':
            return result
        elif (result.categ_id.create_orderpoints == 'yes' or
                self.env.user.company_id.create_orderpoints):
            create = True
        if create:
            company = self.env.user.company_id
            warehouses = wh_obj.search([('company_id', '=', company.id)])
            for warehouse in warehouses:
                orderpoint_obj.create(
                    {'name': result.name,
                     'product_id': result.id,
                     'product_max_qty': company.orderpoint_product_max_qty,
                     'product_min_qty': company.orderpoint_product_min_qty,
                     'warehouse_id': warehouse.id,
                     'location_id': warehouse.lot_stock_id.id
                     })
        return result


class ProductCategory(models.Model):
    _inherit = 'product.category'

    create_orderpoints = fields.Selection(
        selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        string='Create Orderpoints',
        company_dependent=True,
    )
