# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import Counter

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


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

    @api.multi
    def _product_available(self, field_names=None, arg=False):
        res = super(ProductProduct, self)._product_available(
            field_names=field_names, arg=arg)
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        for prod_id in res:
            product = self.browse(prod_id)
            bom_id = bom_obj._bom_find(product_id=prod_id)
            if not bom_id:
                res[prod_id]['potential_qty'] = 0.0
                continue

            bom = bom_obj.browse(bom_id)

            # Need by product (same product can be in many BOM lines/levels)
            component_needs = self._get_components_needs(product, bom)

            if not component_needs:
                # The BoM has no line we can use
                res[prod_id]['potential_qty'] = 0.0

            else:
                # Find the lowest quantity we can make with the stock at hand
                components_potential_qty = min(
                    [self._get_component_qty(component) // need
                     for component, need in component_needs.items()]
                )

                # Compute with bom quantity
                bom_qty = uom_obj._compute_qty_obj(
                    bom.product_uom,
                    bom.product_qty,
                    bom.product_tmpl_id.uom_id
                )
                res[prod_id]['potential_qty'] = bom_qty * \
                                                components_potential_qty
            res[prod_id]['immediately_usable_qty'] =\
                res[prod_id]['potential_qty']
        return res

    @api.multi
    def _get_potential_qty(self):
        """Compute the potential qty based on the available components."""
        res = self._product_available()
        for prod in self:
            prod.potential_qty = res[prod.id]['potential_qty']

    def _get_component_qty(self, component):
        """ Return the component qty to use based en company settings.

        :type component: product_product
        :rtype: float
        """
        icp = self.env['ir.config_parameter']
        stock_available_mrp_based_on = icp.get_param(
            'stock_available_mrp_based_on', 'qty_available'
        )

        return component[stock_available_mrp_based_on]

    def _get_components_needs(self, product, bom):
        """ Return the needed qty of each compoments in the *bom* of *product*.

        :type product: product_product
        :type bom: mrp_bom
        :rtype: collections.Counter
        """
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        product_obj = self.env['product.product']

        needs = Counter()
        for bom_component in bom_obj._bom_explode(bom, product, 1.0)[0]:
            product_uom = uom_obj.browse(bom_component['product_uom'])
            component = product_obj.browse(bom_component['product_id'])

            component_qty = uom_obj._compute_qty_obj(
                product_uom,
                bom_component['product_qty'],
                component.uom_id,
            )
            needs += Counter(
                {component: component_qty}
            )

        return needs
