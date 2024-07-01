# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackageTypeCategory(models.Model):

    _name = "stock.package.type.category"
    _description = "Stock Package Type Category"

    name = fields.Char(translate=True, required=True)
    code = fields.Char(required=True)

    _sql_constraints = [
        (
            "code_unique",
            "unique(code)",
            "The package type category code should be unique",
        )
    ]
