# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventoryLineReason(models.Model):
    _inherit = 'stock.inventory.line.reason'

    virtual_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Virtual Adjustment Location',
        domain=[('usage', 'like', 'inventory')],
    )
