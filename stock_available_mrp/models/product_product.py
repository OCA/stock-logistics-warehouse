# Copyright 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import Counter

from odoo import api, models
from odoo.fields import first
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends("virtual_available", "bom_ids", "bom_ids.product_qty")
    def _compute_available_quantities(self):
        super()._compute_available_quantities()

    def _compute_available_quantities_dict(self):
        res, stock_dict = super()._compute_available_quantities_dict()
        # compute qty for product with bom
        product_with_bom = self.filtered("bom_ids")

        if not product_with_bom:
            return res, stock_dict
        icp = self.env["ir.config_parameter"]
        stock_available_mrp_based_on = icp.sudo().get_param(
            "stock_available_mrp_based_on", "qty_available"
        )

        # explode all boms at once
        exploded_boms = product_with_bom._explode_boms()

        # extract the list of product used as bom component
        component_products = self.env["product.product"].browse()
        for exploded_components in exploded_boms.values():
            for bom_component in exploded_components:
                component_products |= first(bom_component).product_id

        # Compute stock for product components.
        # {'productid': {field_name: qty}}
        if res and stock_available_mrp_based_on in list(res.values())[0]:
            # If the qty is computed by the same method use it to avoid
            # stressing the cache
            component_qties, _ = component_products._compute_available_quantities_dict()
        else:
            # The qty is a field computed by an other method than the
            # current one. Take the value on the record.
            component_qties = {
                p.id: {stock_available_mrp_based_on: p[stock_available_mrp_based_on]}
                for p in component_products
            }

        for product in product_with_bom:
            # Need by product (same product can be in many BOM lines/levels)
            bom_id = first(product.bom_ids)
            exploded_components = exploded_boms[product.id]
            component_needs = product._get_components_needs(exploded_components)
            if not component_needs:
                # The BoM has no line we can use
                potential_qty = immediately_usable_qty = 0.0
            else:
                # Find the lowest quantity we can make with the stock at hand
                components_potential_qty = min(
                    [
                        component_qties[component.id][stock_available_mrp_based_on]
                        / need
                        for component, need in component_needs.items()
                    ]
                )
                potential_qty = bom_id.product_qty * components_potential_qty
                potential_qty = potential_qty > 0.0 and potential_qty or 0.0

                # We want to respect the rounding factor of the potential_qty
                # Rounding down as we want to be pesimistic.
                potential_qty = bom_id.product_uom_id._compute_quantity(
                    potential_qty,
                    bom_id.product_tmpl_id.uom_id,
                    rounding_method="DOWN",
                )

            res[product.id]["potential_qty"] = potential_qty
            immediately_usable_qty = potential_qty if bom_id.type != "phantom" else 0
            res[product.id]["immediately_usable_qty"] += immediately_usable_qty

        return res, stock_dict

    def _explode_boms(self):
        """
        return a dict by product_id of exploded bom lines
        :return:
        """
        return self.explode_bom_quantities()

    @api.model
    def _get_components_needs(self, exploded_components):
        """Return the needed qty of each compoments in the exploded_components

        :type exploded_components
        :rtype: collections.Counter
        """
        needs = Counter()
        for bom_line, bom_qty in exploded_components:
            component = bom_line.product_id
            needs += Counter({component: bom_qty})

        return needs

    def explode_bom_quantities(self):
        """Explode a bill of material with quantities to consume

        It returns a dict with the exploded bom lines and
        the quantity they consume. Example::

            {
            <product-id>: [
                    (<bom-line-id>, <quantity>)
                    (<bom-line-id>, <quantity>)
                ]
            }

        The 'MrpBom.explode()' method includes the same information, with other
        things, but is under-optimized to be used for the purpose of this
        module. The killer is particularly the call to `_bom_find()` which can
        generate thousands of SELECT for searches.
        """
        result = {}

        for product in self:
            lines_done = []
            bom_lines = [
                (first(product.bom_ids), bom_line, product, 1.0)
                for bom_line in first(product.bom_ids).bom_line_ids
            ]

            while bom_lines:
                (current_bom, current_line, current_product, current_qty) = bom_lines[0]
                bom_lines = bom_lines[1:]

                if current_line._skip_bom_line(current_product):
                    continue

                line_quantity = current_qty * current_line.product_qty

                sub_bom = first(current_line.product_id.bom_ids)
                if sub_bom.type == "phantom":
                    product_uom = current_line.product_uom_id
                    converted_line_quantity = product_uom._compute_quantity(
                        line_quantity / sub_bom.product_qty,
                        sub_bom.product_uom_id,
                    )
                    bom_lines = [
                        (
                            sub_bom,
                            line,
                            current_line.product_id,
                            converted_line_quantity,
                        )
                        for line in sub_bom.bom_line_ids
                    ] + bom_lines
                else:
                    # We round up here because the user expects that if he has
                    # to consume a little more, the whole UOM unit should be
                    # consumed.
                    rounding = current_line.product_uom_id.rounding
                    line_quantity = float_round(
                        line_quantity,
                        precision_rounding=rounding,
                        rounding_method="UP",
                    )
                    lines_done.append((current_line, line_quantity))

            result[product.id] = lines_done

        return result
