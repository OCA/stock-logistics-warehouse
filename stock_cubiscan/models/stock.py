# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    cubiscan_device_ids = fields.One2many(
        'cubiscan.device', 'warehouse_id', string="Cubiscan Devices"
    )


class ProductPackaging(models.Model):
    _inherit = "product.packaging"
    _sql_constraints = [
        (
            'product_packaging_type_unique',
            'unique (product_id, packaging_type_id)',
            'It is forbidden to have different packagings '
            'with the same type for a given product.',
        )
    ]

    # TODO move these in an addon. Warning:
    # * 'delivery' defines the same fields and add them in the 'Delivery
    #   Packages' view
    # * our put-away modules (wms/stock_putaway_storage_type_strategy) will
    #   need these fields as well
    max_weight = fields.Float()
    length = fields.Integer('Length (mm)', help='length in millimeters')
    width = fields.Integer('Width (mm)', help='width in millimeters')
    height = fields.Integer('Height (mm)', help='height in millimeters')
    volume = fields.Float(
        'Volume (m³)',
        digits=(8, 4),
        compute='_compute_volume',
        readonly=True,
        store=False,
        help='volume in cubic meters',
    )

    @api.depends('length', 'width', 'height')
    def _compute_volume(self):
        for pack in self:
            pack.volume = (
                pack.length * pack.width * pack.height
            ) / 1000.0 ** 3
