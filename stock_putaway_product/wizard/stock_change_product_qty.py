# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    # When a user updates stock qty on the product form, propose the
    # right location to update stock.
    @api.model
    def default_get(self, fields):
        res = super(StockChangeProductQty, self).default_get(fields)

        product_product_id = res.get('product_id')
        location_id = res.get('location_id')
        new_location_id = False

        if product_product_id and location_id:
            putaway_ids = self.env['stock.product.putaway.strat'].search([
                ('product_product_id', '=', product_product_id),
                ('fixed_location_id', 'child_of', location_id),
            ])
            if len(putaway_ids) > 1:
                raise ValidationError(
                    _('Error!'),
                    _('Multiple fixed locations for this product!')
                )
            new_location_id = putaway_ids.fixed_location_id.id

        if new_location_id:
            res.update({'location_id': new_location_id})

        return res
