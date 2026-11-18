# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "stock.product.secondary.unit.mixin"]
    _name = "product.template"

    stock_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        domain="[('product_tmpl_id', '=', id), ('product_id', '=', False)]",
        string="Second unit for inventory",
        compute="_compute_stock_secondary_uom_id",
        inverse="_inverse_stock_secondary_uom_id",
        store=True,
    )

    def _get_stock_secondary_uom_variants(self):
        self.ensure_one()
        # An archived template only has archived variants
        return (
            self.product_variant_ids
            or self.with_context(active_test=False).product_variant_ids
        )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.active",
        "product_variant_ids.stock_secondary_uom_id",
    )
    def _compute_stock_secondary_uom_id(self):
        for template in self:
            secondary_uom = (
                template._get_stock_secondary_uom_variants().stock_secondary_uom_id
            )
            template.stock_secondary_uom_id = (
                secondary_uom if len(secondary_uom) == 1 else False
            )

    def _inverse_stock_secondary_uom_id(self):
        # Archived variants too: they are the only ones of an archived template,
        # and reactivated ones keep the value
        for template in self:
            template.with_context(
                active_test=False
            ).product_variant_ids.stock_secondary_uom_id = (
                template.stock_secondary_uom_id
            )

    @api.onchange("stock_secondary_uom_id")
    def onchange_stock_secondary_uom_id(self):
        # Archived variants are written too
        variants = self.with_context(active_test=False).product_variant_ids
        if len(variants.stock_secondary_uom_id) > 1:
            return {
                "warning": {
                    "title": self.env._("Warning"),
                    "message": self.env._(
                        "Product variants have distinct second units for inventory:"
                        "\n{secondary_uom}\n"
                        "All variants will be written with the new one"
                    ).format(
                        secondary_uom="\n".join(
                            variants.mapped("stock_secondary_uom_id.name")
                        )
                    ),
                }
            }
