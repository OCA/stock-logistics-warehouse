# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ScrapReasonCode(models.Model):
    _name = "scrap.reason.code"
    _description = "Reason Code"

    name = fields.Char("Code", required=True)
    tag_id = fields.Many2many("stock.scrap.reason.tag", string="Tag")
    description = fields.Text()
    location_id = fields.Many2one(
        "stock.location",
        string="Scrap Location",
        domain="[('usage', '=', 'inventory')]",
        required=True,
    )
    product_category_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        help="Indicate the categories of products that can use this reason code "
        "when doing a scrap. If left empty, this reason code can be used "
        "with any product.",
    )
