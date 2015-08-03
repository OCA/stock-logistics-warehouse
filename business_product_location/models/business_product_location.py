# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class BusinessProductLocation(models.Model):
    _name = 'business.product.location'

    name = fields.Char(string='Name', required=True)
    product_ids = fields.One2many('business.product.line',
                                  'business_product_location_id',
                                  string='Products')
    location_ids = fields.One2many('stock.location',
                                   'business_usage_id',
                                   string='Locations')


class BusinessProductLine(models.Model):
    _name = 'business.product.line'
    _rec_name = "product_id"

    @api.model
    def _default_product_uom_id(self):
        return self.env.ref('product.product_uom_unit')

    product_id = fields.Many2one('product.product', string='Product',
                                 required=True)
    product_qty = fields.Float(
        'Product Quantity', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',
                                     required=True,
                                     default=_default_product_uom_id)
    business_product_location_id = fields.Many2one(
        'business.product.location', 'Parent business product location',
        required=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ Change UoM if product_id changes
        """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id

    @api.onchange('product_uom_id')
    def _onchange_product_uom_id(self):
        """ Check the selected UoM with the product UoM
        """
        res = {}
        if self.product_id and self.product_uom_id:
            if self.product_id.uom_id.category_id.id != \
                    self.product_uom_id.category_id.id:
                res['warning'] = {
                    'title': _('Warning'),
                    'message': _('The Product Unit of Measure you chose '
                                 'has a different category than in the '
                                 'product form.')}
                self.product_uom_id = self.product_id.uom_id


class Product(models.Model):
    _inherit = 'product.product'

    business_usage_ids = fields.One2many('business.product.line', 'product_id',
                                         'Business Usage')


class StockLocation(models.Model):
    _inherit = 'stock.location'

    business_usage_id = fields.Many2one('business.product.location',
                                        'Business Usage')
