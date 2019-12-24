# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class StockLocationLimit(models.Model):
    _name = 'stock.location.limit'
    _description = 'Stock Location Limit Product'
    _rec_name = 'product_id'

    @api.onchange('product_id')
    def onchange_uom_id(self):
        self.uom_id = self.product_id.uom_id.id

    @api.constrains('product_id', 'uom_id')
    def check_uom_id(self):
        if self.uom_id.category_id != self.product_id.uom_id.category_id:
            raise ValidationError(_(
                "The unit of measure for the limit with the product %s must "
                "be in the uom category %s!") %
                (self.product_id.name,
                 self.product_id.uom_id.category_id.name))

    _sql_constraints = [
        ('product_uniq', 'unique(product_id,location_id)',
         'You cannot set 2 limits with the same product for a location!')]

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float('Maximum Quantity',
                       digits=dp.get_precision('Product Quantity'))
    uom_id = fields.Many2one('uom.uom', string='UoM')
    location_id = fields.Many2one('stock.location', string='Location')
