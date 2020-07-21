# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    cubiscan_device_ids = fields.One2many(
        "cubiscan.device", "warehouse_id", string="Cubiscan Devices"
    )
