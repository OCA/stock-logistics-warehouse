# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    location_dest_id = fields.Many2one(
        comodel_name='stock.location', string='Finished Products Location',
        domain="[('id', 'child_of', location_id)]")
