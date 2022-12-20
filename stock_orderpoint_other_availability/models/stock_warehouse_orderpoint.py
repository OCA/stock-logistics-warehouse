#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockWarehouseOrderpoint (models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        location_id = res.get('location_id')
        if location_id:
            res['other_availability_location_id'] = location_id
        return res

    is_other_availability = fields.Boolean(
        string="Check availability of another product",
    )
    other_availability_product_id = fields.Many2one(
        comodel_name='product.product',
        domain=[
            ('type', '=', 'product'),
        ],
        string="Product for availability",
        help="This inventory rule will also be triggered "
             "based on the availability of this product.",
    )
    other_availability_qty = fields.Float(
        string="Minimum Availability",
        help="This inventory rule will also be triggered "
             "when the availability of 'Product for availability' "
             "is below this quantity.",
        digits=dp.get_precision('Product Unit of Measure'),
    )
    other_availability_location_id = fields.Many2one(
        comodel_name='stock.location',
        string="Location for availability",
        help="This inventory rule will also be triggered "
             "based on the availability in this location.",
    )
