# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    """Add a field for the stock available to promise.
    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """
    _inherit = 'product.template'

    # immediately usable quantity caluculated with the quant method
    @api.multi
    @api.depends('virtual_available')
    def _immediately_usable_qty(self):
        stock_location_obj = self.env['stock.location']
        internal_locations = stock_location_obj.search([
            ('usage', '=', 'internal')])
        sublocations = self.env['stock.location']
        for location in internal_locations:
            sublocations += stock_location_obj.search(
                [('id', 'child_of', location.id)])
        for product_template in self:
            products = self.env['product.product'].search([
                ('product_tmpl_id', '=', product_template.id)])
            quant_obj = self.env['stock.quant']
            quants = quant_obj.search([
                ('location_id', 'in', sublocations.ids),
                ('product_id', 'in', products.ids),
                ('reservation_id', '=', False)])
            availability = 0
            if quants:
                for quant in quants:
                    availability += quant.qty
            product_template.immediately_usable_qty = availability

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_immediately_usable_qty',
        string='Available to promise (quant calculation)',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs , this number is obtained by using the new odoo 8 "
             "quants, so it gives us the actual current quants  minus reserved"
             "quants")
