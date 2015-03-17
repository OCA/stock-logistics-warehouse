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

    @api.depends('virtual_available')
    def _product_available(self):
        """No-op implementation of the stock available to promise.

        By default, available to promise = forecasted quantity.

        Must be overridden by another module that actually implement
        computations."""
        for product in self:
            product.immediately_usable_qty = product.virtual_available

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_product_available',
        string='Available to promise',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs")
