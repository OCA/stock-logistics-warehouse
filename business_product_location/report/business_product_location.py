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

from openerp import api, models
from openerp.tools.float_utils import float_compare


class BusinessProductLocationReport(models.AbstractModel):
    _name = 'report.business_product_location.report_bpl'

    @api.model
    def _get_more_product(self, location, less_product):
        more_product = {}
        product_obj = self.env['product.product']
        product_in_loc = product_obj.with_context(
            location=location.id).search([('qty_available', '>', 0)])
        for product in product_in_loc:
            # get the product to update the quantity or create a new entry
            product_to_update = less_product.get(
                product.id,
                {'product_name': product.display_name,
                 'excepted_qty': 0,
                 'real_qty': 0,
                 'outgoing_qty': 0,
                 'strong': True})
            product_to_update['real_qty'] = product.qty_available
            product_to_update['outgoing_qty'] = product.outgoing_qty

            # check if there is a quantity difference to adapt the display
            # of the line in the report (strong or not)
            real_less_outgoing_qty = (product_to_update['real_qty'] -
                                      product_to_update['outgoing_qty'])
            if float_compare(
                    product_to_update['excepted_qty'], real_less_outgoing_qty,
                    precision_rounding=1) == 0:
                product_to_update['strong'] = False
            # if the product is not in the list of product, add it to the
            # the list more_product
            if product.id not in less_product.keys():
                more_product[product.id] = product_to_update
        return more_product

    @api.model
    def _get_less_product(self, location):
        """ get all products defined in the business usage
        """
        less_product_by_loc = {}
        for product_line in location.business_usage_id.product_ids:
            less_product_by_loc[product_line.product_id.id] = {
                'product_name': product_line.product_id.display_name,
                'excepted_qty': product_line.product_qty,
                'real_qty': 0,
                'outgoing_qty': 0,
                'strong': True}
        return less_product_by_loc

    @api.model
    def _get_product_by_loc(self, locations):
        less_product_by_loc = {}
        more_product_by_loc = {}

        for location in locations:
            # report should contains only location with a business usage
            if not location.business_usage_id:
                continue
            # compose the key of dictionary with a location_id
            # and business_usage_id
            location_business_id = (location.id,
                                    location.business_usage_id.id)
            # compute the display location - business usage for the report
            location_name = '%s - %s' % (location.name,
                                         location.business_usage_id.name)
            # compute products list
            less_product = self._get_less_product(location)
            more_product = self._get_more_product(location, less_product)
            less_product_by_loc[location_business_id] = {
                'location_name': location_name,
                'products': less_product}
            more_product_by_loc[location_business_id] = {
                'location_name': location_name,
                'products': more_product}

        return (less_product_by_loc, more_product_by_loc)

    @api.multi
    def render_html(self, data=None):
        """ Get the list of product excepted in the location and the list of
            product in the location with the quantity
        """
        docs = self.env['stock.location'].browse(self._ids)

        (less_product_by_loc,
         more_product_by_loc) = self._get_product_by_loc(docs)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': 'stock.location',
            'docs': docs,
            'less_product_by_loc': less_product_by_loc,
            'more_product_by_loc': more_product_by_loc,
        }
        return self.env['report'].render(
            'business_product_location.report_bpl', docargs)
