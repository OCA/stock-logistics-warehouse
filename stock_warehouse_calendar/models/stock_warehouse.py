# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    calendar_id = fields.Many2one('resource.calendar',
                                  'Working Hours')

    partner_tz = fields.Selection(related='partner_id.tz')
