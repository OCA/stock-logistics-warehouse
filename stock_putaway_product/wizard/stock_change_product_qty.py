# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    # When a user updates stock qty on the product form, propose the
    # right location to update stock.
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        product_product_id = res.get('product_id')
        location_id = res.get('location_id')

        if product_product_id and location_id:
            putaway = self.env['stock.product.putaway.strategy'].search([
                ('product_product_id', '=', product_product_id),
                ('fixed_location_id', 'child_of', location_id),
            ], limit=1)
            if putaway:
                res.update({'location_id': putaway.fixed_location_id.id})

        return res
