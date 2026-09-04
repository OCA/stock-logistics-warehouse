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
        readonly=False,
    )

    @api.depends("product_variant_ids.stock_secondary_uom_id")
    def _compute_stock_secondary_uom_id(self):
        self._compute_template_secondary_uom_field("stock_secondary_uom_id")

    def _inverse_stock_secondary_uom_id(self):
        self._inverse_template_secondary_uom_field("stock_secondary_uom_id")
