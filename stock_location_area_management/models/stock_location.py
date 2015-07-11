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


class StockLocation(models.Model):
    """
    Add the area dimension and the unit of measure of the warehouse locations.
    By default, the unit of measure is the one of the user's company.
    Add a boolean for the form view in order to display or not area
    dimensions fields.
    """
    _inherit = 'stock.location'

    area_dimension = fields.Integer('Dimension')

    active_dimension = fields.Boolean('Area Dimension')

    def _get_company_locations_uom(self):
        """
        Get the unit of measure of the user's company locations
        :return: Unit of measure of the user's company
        """
        return self.env['res.users'].browse(self._uid).company_id.locations_uom

    location_uom = fields.Many2one(
        string='Unit of Measure',
        comodel_name='product.uom',
        help='This field corresponds to the unit of measure of the location',
        domain="[('category_id.name','=','Surface')]",
        default=lambda self: self._get_company_locations_uom(),
    )
