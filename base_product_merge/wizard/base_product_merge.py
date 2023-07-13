# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade_merge_records

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BaseProductMerge(models.Model):
    _name = "base.product.merge"
    _description = "Merges two products"

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self.env.context.get("active_ids", False)
        active_model = self.env.context.get("active_model", False)
        ptype = active_model
        rec.update({"ptype": ptype})
        if ptype == "product.product":
            products = self.env[active_model].browse(active_ids)
            rec.update({"product_ids": [(6, 0, products.ids)]})
        else:
            product_templates = self.env[active_model].browse(active_ids)
            rec.update({"product_tmpl_ids": [(6, 0, product_templates.ids)]})
        return rec

    dst_product_id = fields.Many2one("product.product", string="Destination product")
    product_ids = fields.Many2many(
        "product.product",
        "product_rel",
        "product_merge_id",
        "product_id",
        string="Products to merge",
    )
    ptype = fields.Selection(
        [("product.product", "Product"), ("product.template", "Template")]
    )
    dst_product_tmpl_id = fields.Many2one(
        "product.template", string="Destination product"
    )
    product_tmpl_ids = fields.Many2many(
        "product.template",
        "product_tmpl_rel",
        "product_tmpl_merge_id",
        "product_tmpl_id",
        string="Products to merge",
    )
    merge_method = fields.Selection([("sql", "SQL"), ("orm", "ORM")], default="sql")

    def action_merge(self):
        if self.ptype == "product.product":
            dst_product = self.dst_product_id
            products_to_merge = self.product_ids - dst_product
        else:
            dst_product = self.dst_product_tmpl_id
            products_to_merge = self.product_tmpl_ids - dst_product
            # merge product first when there is template with single product
            if not any(
                products_to_merge.product_variant_ids.mapped("combination_indices")
            ):
                dst_product_product = self.dst_product_tmpl_id.product_variant_id
                product_product_to_merge = (
                    self.product_tmpl_ids.product_variant_ids - dst_product_product
                )
                if not product_product_to_merge:
                    raise UserError(_("You cannot merge product to it self."))
                self.merge_products(
                    "product.product", product_product_to_merge, dst_product_product
                )
        self.merge_products(self.ptype, products_to_merge, dst_product)

    def merge_products(self, model, products_to_merge, dst_product):
        try:
            if not products_to_merge:
                raise UserError(_("You cannot merge product to it self."))
            openupgrade_merge_records.merge_records(
                self.env,
                model,
                products_to_merge.ids,
                dst_product.id,
                method=self.merge_method,
            )
        except Exception as e:
            _logger.warning(e)
            raise UserError(_("Error occurred while merging products.")) from e
