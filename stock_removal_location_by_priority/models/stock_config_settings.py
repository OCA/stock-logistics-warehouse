# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    removal_priority_active = fields.Boolean(
        related='company_id.removal_priority_active',
        string="Use 'Removal Priority' in Locations (*)",
        help="This configuration is related to the company you're logged into")
