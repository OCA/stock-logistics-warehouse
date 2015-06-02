# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import models, fields


class ResCompany(models.Model):
    """
    Add the unit of measure of the warehouse locations.
    Set by default to m².
    """
    _inherit = 'res.company'

    def _get_default_locations_uom(self):
        """
        Get the unit of measure m² (default)
        :return: Unit of measure m²
        """
        return self.env.ref('stock_location_area_data.product_uom_m2')

    locations_uom = fields.Many2one(
        string='Unit of Measure',
        comodel_name='product.uom',
        help='This field corresponds to the unit of measure of the warehouse '
             'locations',
        domain="[('category_id.name','=','Surface')]",
        default=lambda self: self._get_default_locations_uom(),
    )
