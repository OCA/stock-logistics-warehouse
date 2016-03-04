# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import Counter

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp
from openerp.tools.safe_eval import safe_eval


class ProductProduct(models.Model):
    _inherit = 'product.product'

    potential_qty = fields.Float(
        compute='_get_potential_qty',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Potential',
        help="Quantity of this Product that could be produced using "
             "the materials already at hand.")

    @api.multi
    @api.depends('potential_qty')
    def _immediately_usable_qty(self):
        """Add the potential quantity to the quantity available to promise.

        This is the same implementation as for templates."""
        super(ProductProduct, self)._immediately_usable_qty()
        for product in self:
            product.immediately_usable_qty += product.potential_qty

    @api.multi
    def _get_potential_qty(self):
        """Compute the potential qty based on the available components."""
        bom_obj = self.env['mrp.bom']
        icp = self.env['ir.config_parameter']
        stock_available_mrp_based_on = safe_eval(
            icp.get_param('stock_available_mrp_based_on', 'False'))
        if not stock_available_mrp_based_on:
            stock_available_mrp_based_on = 'qty_available'

        for product in self:
            bom_id = bom_obj._bom_find(product_id=product.id)
            if not bom_id:
                product.potential_qty = 0.0
                continue

            # Need by product (same product can be in many BOM lines/levels)
            component_needs = Counter()
            for component in bom_obj._bom_explode(bom_obj.browse(bom_id),
                                                  product, 1.0,)[0]:
                component_needs += Counter(
                    {component['product_id']: component['product_qty']})
            if not component_needs:
                # The BoM has no line we can use
                product.potential_qty = 0.0
                continue

            # Find the lowest quantity we can make with the stock at hand
            product.potential_qty = min(
                [getattr(self.browse(component_id),
                         stock_available_mrp_based_on) // need
                 for component_id, need in component_needs.items()])
