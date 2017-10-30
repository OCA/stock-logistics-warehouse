# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    group_removal_priority = fields.Selection([
        (0, 'Don\'t use \'Removal Priority\' in Locations'),
        (1, 'Use \'Removal Priority\' in Locations'),
    ], "Removal Priority",
        implied_group='stock_removal_location_by_priority.'
                      'group_removal_priority',
        help="Removal priority that applies when the incoming dates "
             "are equal in both locations.")
