# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    warehouse_id = fields.Many2one(
        'stock.warehouse', related='location_id.warehouse_id',
        store=True, index=True)
