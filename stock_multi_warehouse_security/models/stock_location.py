# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.depends('location_id')
    def _compute_warehouse(self):
        for location in self:
            location.warehouse_id = location.get_warehouse()

    warehouse_id = fields.Many2one(
        'stock.warehouse', compute='_compute_warehouse',
        store=True, index=True)
