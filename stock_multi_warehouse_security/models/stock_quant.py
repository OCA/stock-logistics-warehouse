# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.depends('location_id')
    # Do not make related field because we do not want to recompute quants
    # if parent of location_id changes...
    def _get_warehouse(self):
        for quant in self:
            quant.warehouse_id = quant.location_id.warehouse_id.id

    warehouse_id = fields.Many2one(
        'stock.warehouse', compute='_get_warehouse',
        store=True, index=True)
