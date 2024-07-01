# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackageType(models.Model):

    _inherit = "stock.package.type"

    category_id = fields.Many2one(
        comodel_name="stock.package.type.category",
        string="Category",
        help="This is the category this package type belongs to",
        index="btree_not_null",
    )
