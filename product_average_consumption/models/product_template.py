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

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_consumption_calculation_method(self):
        return [
            ('moves', 'Moves (calculate consumption based on Stock Moves)'),
        ]

    # Columns Section
    average_consumption = fields.Float(compute='_compute_average_consumption', string='Average Consumption')
    displayed_average_consumption = fields.Float(compute='_displayed_average_consumption', string='Average Consumption')
    total_consumption = fields.Float(compute='_compute_average_consumption', string='Total Consumption')
    nb_days = fields.Integer(compute='_compute_average_consumption', string='Real Calculation Range (days)',
                                help="""The calculation will be done for the last 365 days or"""
                                """ since the first stock move of the product if it's"""
                                """ more recent""")
    consumption_calculation_method = fields.Selection(_get_consumption_calculation_method,
                                                      'Consumption Calculation Method', default='moves')
    display_range = fields.Integer( 'Display Range in days', default=1, help="""Examples:
        1 -> Average Consumption per days
        7 -> Average Consumption per week
        30 -> Average Consumption per month""")
    calculation_range = fields.Integer('Asked Calculation Range (days)', default=365, help=""" Number of days used for the calculation of the average """
        """ consumption. For example: if you put 365, the calculation will """
        """ be done on last year.""")

    # Fields Function Section
    @api.depends('product_variant_ids', 'product_variant_ids.nb_days', 'product_variant_ids.total_consumption',
                 'consumption_calculation_method', 'calculation_range')
    @api.multi
    def _compute_average_consumption(self):
        for template in self:
            if template.consumption_calculation_method == 'moves':
                template._average_consumption_moves()

    @api.multi
    def _average_consumption_moves(self):
        for template in self:
            if template.product_variant_ids:
                nb_days = max(template.product_variant_ids.mapped('nb_days'))
                total_consumption = sum(template.product_variant_ids.mapped('total_consumption'))
                template.nb_days = nb_days
                template.total_consumption = total_consumption
                template.average_consumption = (nb_days and (total_consumption / nb_days) or False)

    @api.depends('display_range', 'average_consumption')
    @api.multi
    def _displayed_average_consumption(self):
        for template in self:
            template.displayed_average_consumption = template.average_consumption * template.display_range
