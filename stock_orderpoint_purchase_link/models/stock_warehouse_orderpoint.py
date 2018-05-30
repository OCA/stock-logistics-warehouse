# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    purchase_line_ids = fields.Many2many(
        comodel_name='purchase.order.line',
        string='Purchase Order Lines', copy=False,
        readonly=True,
    )
