# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPackageType(models.Model):

    _inherit = "stock.package.type"

    category_id = fields.Many2one(
        comodel_name="stock.package.type.category",
        string="Category",
        help="This is the category this package type belongs to",
        index="btree_not_null",
    )

    @api.depends("category_id", "category_id.code")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for package_type in self:
            if package_type.category_id:
                package_type.display_name = " ".join(
                    [
                        package_type.display_name,
                        str("(" + package_type.category_id.code + ")"),
                    ]
                )
        return res

    @property
    def _rec_names_search(self):
        """
        Adds the category code and name in name search
        """
        rec_names_search = super()._rec_names_search
        if not rec_names_search:
            return ["name", "category_id.name", "category_id.code"]
        else:
            rec_names_search.extend(["category_id.name", "category_id.code"])
            return rec_names_search
