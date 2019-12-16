# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocationLimit(models.Model):
    _name = 'stock.location.limit'
    _description = 'Stock Location Limit Product'
    _rec_name = 'product_id'

    _sql_constraints = [
        ('product_uniq', 'unique(product_id,location_id)',
            'Product and Location must be unique!'),
    ]

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    qty = fields.Float('Maximum Quantity')
    uom_id = fields.Many2one(
        'uom.uom',
        related='product_id.uom_id',
        string='UoM',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
