# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    cubiscan_device_ids = fields.One2many(
        'cubiscan.device', 'warehouse_id', string="Cubiscan Devices"
    )


class ProductPackaging(models.Model):
    _inherit = "product.packaging"
    # FIXME: Not sure this is still the best place for this constraint
    _sql_constraints = [
        (
            'product_packaging_type_unique',
            'unique (product_id, packaging_type_id)',
            'It is forbidden to have different packagings '
            'with the same type for a given product.',
        )
    ]
