# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StocklocationContentTemplateLine(models.Model):
    _name = "stock.location.content.template.line"
    _description = "Stock Location Content Template Lines"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    in_checkout = fields.Boolean(string="Included in Checkout?")
    quantity = fields.Float(string="Expected Quantity", required=True)
    uom_id = fields.Many2one(related="product_id.uom_id", string="UoM")
    template_id = fields.Many2one(
        "stock.location.content.template", string="Template", required=True
    )

    _sql_constraints = [
        (
            "template_product_uniq",
            "unique (product_id, template_id)",
            "You cannot have the same product twice on a template!",
        ),
    ]
