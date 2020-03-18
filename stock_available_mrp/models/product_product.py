# Copyright 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import Counter
from odoo import api, fields, models
from odoo.fields import first


class ProductProduct(models.Model):

    _inherit = 'product.product'

    bom_id = fields.Many2one(
        'mrp.bom',
        compute='_compute_bom_id',
        string='Bill of Materials'
    )

    @api.depends('virtual_available', 'bom_id', 'bom_id.product_qty')
    def _compute_available_quantities(self):
        super(ProductProduct, self)._compute_available_quantities()

    @api.multi
    def _get_bom_id_domain(self):
        """
        Real multi domain
        :return:
        """
        return [
            '|',
            ('product_id', 'in', self.ids),
            '&',
            ('product_id', '=', False),
            ('product_tmpl_id', 'in', self.mapped('product_tmpl_id.id'))
        ]

    @api.multi
    @api.depends('product_tmpl_id')
    def _compute_bom_id(self):
        bom_obj = self.env['mrp.bom']
        boms = bom_obj.search(
            self._get_bom_id_domain(),
            order='sequence, product_id',
        )
        for product in self:
            product_boms = boms.filtered(
                lambda b: b.product_id == product or
                (not b.product_id and
                 b.product_tmpl_id == product.product_tmpl_id)
            )
            if product_boms:
                product.bom_id = first(product_boms)

    @api.multi
    def _compute_available_quantities_dict(self):
        res, stock_dict = super(ProductProduct,
                                self)._compute_available_quantities_dict()
        # compute qty for product with bom
        product_with_bom = self.filtered('bom_id')

        if not product_with_bom:
            return res, stock_dict
        icp = self.env['ir.config_parameter']
        stock_available_mrp_based_on = icp.sudo().get_param(
            'stock_available_mrp_based_on', 'qty_available'
        )

        # explode all boms at once
        exploded_boms = product_with_bom._explode_boms()

        # extract the list of product used as bom component
        component_products = self.env['product.product'].browse()
        for exploded_components in exploded_boms.values():
            for bom_component in exploded_components:
                component_products |= first(bom_component).product_id

        # Compute stock for product components.
        # {'productid': {field_name: qty}}
        if res and stock_available_mrp_based_on in list(res.values())[0]:
            # If the qty is computed by the same method use it to avoid
            # stressing the cache
            component_qties, _ = \
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
                exploded_components, only_stockable=True)

            if not component_needs:
                # The BoM has no line we can use
                potential_qty = -1.0
            else:
                # Find the lowest quantity we can make with the stock at hand
                components_potential_qty = min(
                    [component_qties[component.id][
                        stock_available_mrp_based_on] / need
                     for component, need in component_needs.items()]
                )

                bom_id = product.bom_id
                potential_qty = (bom_id.product_qty * components_potential_qty)

                # We want to respect the rounding factor of the potential_qty
                # Rounding down as we want to be pesimistic.
                potential_qty = bom_id.product_uom_id._compute_quantity(
                    potential_qty,
                    product.bom_id.product_tmpl_id.uom_id,
                    rounding_method='DOWN'
                )

            res[product.id]['potential_qty'] = potential_qty
            res[product.id]['immediately_usable_qty'] += potential_qty

        return res, stock_dict

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
    def _get_components_needs(self, exploded_components, only_stockable=False):
        """ Return the needed qty of each compoments in the exploded_components

        :type exploded_components
        :rtype: collections.Counter
        """
        needs = Counter()
        for bom_component in exploded_components:
            component = bom_component[0].product_id
            # ignore 'service' and 'consu' in BoM to set potential_qty=-1.0
            if only_stockable and component.type != "product":
                continue
            needs += Counter({component: bom_component[1]['qty']})

        return needs
