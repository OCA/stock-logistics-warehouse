# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import Counter, defaultdict
from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    bom_id = fields.Many2one(
        'mrp.bom',
        compute='_compute_bom_id',
        string='Bill of Materials'
    )

    @api.depends('virtual_available')
    def _compute_available_quantities(self):
        super(ProductProduct, self)._compute_available_quantities()

    @api.multi
    def _compute_bom_id(self):
        domain = [('product_id', 'in', self.ids)]
        product_tmpl_ids = []
        bom_product_ids = self.env['mrp.bom'].search(domain)
        # find bom linked to a product
        bom_by_product_id = {
            b.product_id.id: b for b in bom_product_ids}
        product_id_found = bom_by_product_id.keys()
        for product in self:
            if product.id not in product_id_found:
                product_tmpl_ids.append(product.product_tmpl_id.id)
        domain = [('product_id', '=', False),
                  ('product_tmpl_id', 'in', product_tmpl_ids)]
        # find boms linked to the product template
        bom_product_template = self.env['mrp.bom'].search(domain)
        bom_by_product_tmpl_id = {
            b.product_tmpl_id.id: b for b in bom_product_template}
        for product in self:
            product.bom_id = bom_by_product_id.get(
                product.id,
                bom_by_product_tmpl_id.get(product.product_tmpl_id.id)
            )

    @api.multi
    def _compute_available_quantities_dict(self):
        res = super(ProductProduct, self)._compute_available_quantities_dict()

        # compute qty for product with bom
        product_with_bom = self.filtered(lambda p: p.bom_id)

        if not product_with_bom:
            return res
        icp = self.env['ir.config_parameter']
        stock_available_mrp_based_on = icp.get_param(
            'stock_available_mrp_based_on', 'qty_available'
        )

        # from here we start the computation of bom qties in an isolated
        # environment to avoid trouble with prefetch and cache
        product_with_bom = product_with_bom.with_context(
            unique=models.NewId()).with_prefetch(defaultdict(set))

        # explode all boms at once
        exploded_boms = product_with_bom._explode_boms()

        # extract the list of product used as bom component
        product_components_ids = set()
        for exploded_components in exploded_boms.values():
            for bom_component in exploded_components:
                product_components_ids.add(bom_component[0].product_id.id)

        # Compute stock for product components.
        # {'productid': {field_name: qty}}
        component_products = product_with_bom.browse(
            product_components_ids)
        if stock_available_mrp_based_on in res.keys():
            # If the qty is computed by the same method use it to avoid
            # stressing the cache
            component_qties = \
                component_products._compute_available_quantities_dict()
        else:
            # The qty is a field computed by an other method than the
            # current one. Take the value on the record.
            component_qties = {
                p.id: {
                    stock_available_mrp_based_on: p[
                        stock_available_mrp_based_on]} for p in
                component_products}

        for product in product_with_bom:
            # Need by product (same product can be in many BOM lines/levels)
            exploded_components = exploded_boms[product.id]
            component_needs = product._get_components_needs(
                exploded_components)
            if not component_needs:
                # The BoM has no line we can use
                potential_qty = 0.0

            else:
                # Find the lowest quantity we can make with the stock at hand
                components_potential_qty = min(
                    [component_qties[component.id][
                        stock_available_mrp_based_on] // need
                     for component, need in component_needs.items()]
                )

                potential_qty = (product.bom_id.product_qty *
                                 components_potential_qty)

            res[product.id]['potential_qty'] = potential_qty
            res[product.id]['immediately_usable_qty'] += potential_qty

        return res

    @api.multi
    def _explode_boms(self):
        """
        return a dict by product_id of exploded bom lines
        :return:
        """
        exploded_boms = {}
        for rec in self:
            exploded_boms[rec.id] = rec.bom_id.explode(rec, 1.0)[1]
        return exploded_boms

    @api.model
    def _get_components_needs(self, exploded_components):
        """ Return the needed qty of each compoments in the exploded_components

        :type exploded_components
        :rtype: collections.Counter
        """
        needs = Counter()
        for bom_component in exploded_components:
            component = bom_component[0].product_id
            needs += Counter({component: bom_component[1]['qty']})

        return needs
