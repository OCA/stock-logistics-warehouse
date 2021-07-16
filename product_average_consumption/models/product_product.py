##############################################################################
#
#    Product - Average Consumption Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

import time
import datetime
from odoo import models, fields, api
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Columns Section
    average_consumption = fields.Float(compute='_compute_average_consumption')
    displayed_average_consumption = fields.Float(
        compute='_compute_displayed_average_consumption',
        string='Average Consumption (Range)',
    )
    total_consumption = fields.Float(compute='_compute_average_consumption')
    nb_days = fields.Integer(
        compute='_compute_average_consumption',
        string='Number of days for the calculation',
        help="""The calculation will be done according to Calculation Range"""
        """ field or since the first stock move of the product if it's"""
        """ more recent""")
    consumption_calculation_method = fields.Selection(
        related='product_tmpl_id.consumption_calculation_method')
    display_range = fields.Integer(related='product_tmpl_id.display_range')
    calculation_range = fields.Integer(
        related='product_tmpl_id.calculation_range')

    # Private Function Section
    @api.model
    def _min_date(self, product_id):
        query = """SELECT to_char(min(date), 'YYYY-MM-DD') \
                from stock_move where product_id = %s"""
        cr = self.env.cr
        cr.execute(query, (product_id, ))
        results = cr.fetchall()
        return results and results[0] and results[0][0] \
            or time.strftime('%Y-%m-%d')

    # Fields Function Section
    @api.depends('consumption_calculation_method', 'calculation_range')
    def _compute_average_consumption(self):
        for product in self:
            if product.consumption_calculation_method == 'moves':
                product._average_consumption_moves()

    def _get_domain_dates(self):
        from_date = self._context.get('from_date', False)
        to_date = self._context.get('to_date', False)
        domain = []
        if from_date:
            domain.append(('date', '>=', from_date))
        if to_date:
            domain.append(('date', '<=', to_date))
        return domain

    # @api.onchange('calculation_range')
    # @api.multi
    def _average_consumption_moves(self):
        dql, dmil, domain_move_out_loc = self._get_domain_locations()
        domain_move_out = [('state', 'not in', ('cancel', 'draft'))]
        if self._context.get('owner_id'):
            domain_move_out.append(
                ('restrict_partner_id', '=', self._context['owner_id']))
        domain_move_out += domain_move_out_loc
        for product in self:
            begin_date = (datetime.datetime.today() - datetime.timedelta(
                days=product.calculation_range)).strftime('%Y-%m-%d')
            first_date = max(begin_date, self._min_date(product.id))
            domain_move_out = self.with_context(
                from_date=first_date)._get_domain_dates() + \
                [('product_id', '=', product.id)] + \
                domain_move_out
            moves_out = self.env['stock.move'].read_group(
                domain_move_out, ['product_id', 'product_qty'], ['product_id'])
            moves_out = dict([(x['product_id'][0], x['product_qty'])
                              for x in moves_out])
            outgoing_qty = float_round(
                moves_out.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding)
            nb_days = (datetime.datetime.today() -
                       datetime.datetime.strptime(first_date, '%Y-%m-%d')).days
            product.average_consumption = \
                (nb_days and (outgoing_qty / nb_days) or False)
            product.total_consumption = outgoing_qty or False
            product.nb_days = nb_days or False

    @api.depends('display_range', 'average_consumption')
    @api.multi
    def _compute_displayed_average_consumption(self):
        for product in self:
            product.displayed_average_consumption = \
                product.average_consumption * product.display_range
