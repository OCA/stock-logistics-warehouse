# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    potential_qty = fields.Float(
        compute='_get_potential_qty',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Potential',
        help="Quantity of this Product that could be produced using "
             "the materials already at hand. "
             "If the product has several variants, this will be the biggest "
             "quantity that can be made for a any single variant.")

    @api.multi
    def _product_available(self, name=None, arg=False):
        res = super(ProductTemplate, self)._product_available(name, arg)

        variants = self.env['product.product']
        for tmpl in self:
            variants += tmpl.product_variant_ids
        variant_available = variants._product_available()

        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                # useless computation when product only exists in cache
                continue
            potential_qty = 0.0
            if tmpl.bom_ids:
                for p in tmpl.product_variant_ids:
                    if potential_qty <\
                            variant_available[p.id]["potential_qty"]:
                        potential_qty = variant_available[p.id][
                            "potential_qty"]
                res[tmpl.id]['immediately_usable_qty'] = potential_qty
            res[tmpl.id].update({"potential_qty": potential_qty})
        return res

    @api.multi
    @api.depends('potential_qty')
    def _immediately_usable_qty(self):
        """Add the potential quantity to the quantity available to promise.

        This is the same implementation as for variants."""
        res = self._product_available()
        for tmpl in self.filtered(lambda x: not isinstance(
                x.id, models.NewId)):
            tmpl.immediately_usable_qty = res[tmpl.id][
                'immediately_usable_qty']

    @api.multi
    @api.depends('product_variant_ids.potential_qty')
    def _get_potential_qty(self):
        """Compute the potential as the max of all the variants's potential.

        We can't add the potential of variants: if they share components we
        may not be able to make all the variants.
        So we set the arbitrary rule that we can promise up to the biggest
        variant's potential.
        """
        res = self._product_available()
        for tmpl in self.filtered(lambda x: not isinstance(
                x.id, models.NewId)):
            tmpl.potential_qty = res[tmpl.id]['potential_qty']
