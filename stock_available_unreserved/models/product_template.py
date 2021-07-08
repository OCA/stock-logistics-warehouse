# Copyright 2018 Camptocamp SA
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string="Quantity On Hand Unreserved",
        digits="Product Unit of Measure",
        compute="_compute_product_available_not_res",
        search="_search_quantity_unreserved",
        help="Quantity of this product that is "
        "not currently reserved for a stock move",
    )

    @api.depends("product_variant_ids.qty_available_not_res")
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(
                tmpl.mapped("product_variant_ids.qty_available_not_res")
            )

    def action_open_quants_unreserved(self):
        products_ids = self.mapped("product_variant_ids").ids
        quants = self.env["stock.quant"].search([("product_id", "in", products_ids)])
        quant_ids = quants.filtered(
            lambda x: x.product_id.qty_available_not_res > 0
        ).ids
        result = self.env.ref("stock.group_stock_multi_locations").read()[0]
        result["domain"] = [("id", "in", quant_ids)]
        result["context"] = {
            "search_default_locationgroup": 1,
            "search_default_internal_loc": 1,
        }
        return result

    def _search_quantity_unreserved(self, operator, value):
        return [("product_variant_ids.qty_available_not_res", operator, value)]
