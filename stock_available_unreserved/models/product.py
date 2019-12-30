# Copyright 2018 Camptocamp SA
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

from odoo.addons.stock.models.product import OPERATORS


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string="Quantity On Hand Unreserved",
        digits="Product Unit of Measure",
        compute="_compute_product_available_not_res",
        search="_search_quantity_unreserved",
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
        result = self.env.ref("stock.product_template_open_quants").read()[0]
        result["domain"] = [("id", "in", quant_ids)]
        result["context"] = {
            "search_default_locationgroup": 1,
            "search_default_internal_loc": 1,
        }
        return result

    def _search_quantity_unreserved(self, operator, value):
        domain = [("qty_available_not_res", operator, value)]
        product_variant_ids = self.env["product.product"].search(domain)
        return [("product_variant_ids", "in", product_variant_ids.ids)]


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available_not_res = fields.Float(
        string="Qty Available Not Reserved",
        digits="Product Unit of Measure",
        compute="_compute_qty_available_not_reserved",
        search="_search_quantity_unreserved",
    )

    def _prepare_domain_available_not_reserved(self):
        domain_quant = [("product_id", "in", self.ids)]
        domain_quant_locations = self._get_domain_locations()[0]
        domain_quant.extend(domain_quant_locations)
        return domain_quant

    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_reserved()
        quants = (
            self.env["stock.quant"]
            .with_context(lang=False)
            .read_group(
                domain_quant,
                ["product_id", "location_id", "quantity", "reserved_quantity"],
                ["product_id", "location_id"],
                lazy=False,
            )
        )
        product_sums = {}
        for quant in quants:
            # create a dictionary with the total value per products
            product_sums.setdefault(quant["product_id"][0], 0.0)
            product_sums[quant["product_id"][0]] += (
                quant["quantity"] - quant["reserved_quantity"]
            )
        for product in self.with_context(prefetch_fields=False, lang=""):
            available_not_res = float_round(
                product_sums.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding,
            )
            res[product.id] = {"qty_available_not_res": available_not_res}
        return res

    @api.depends("stock_move_ids.product_qty", "stock_move_ids.state")
    def _compute_qty_available_not_reserved(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]["qty_available_not_res"]
            prod.qty_available_not_res = qty
        return res

    def _search_quantity_unreserved(self, operator, value):
        if operator not in OPERATORS:
            raise UserError(_("Invalid domain operator %s") % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_("Invalid domain right operand %s") % value)

        ids = []
        for product in self.search([]):
            if OPERATORS[operator](product.qty_available_not_res, value):
                ids.append(product.id)
        return [("id", "in", ids)]
