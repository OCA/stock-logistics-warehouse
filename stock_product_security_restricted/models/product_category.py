# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "restricted.access.mixin"]

    restricted_access = fields.Boolean(
        help="If checked, only users with restricted access can modify this record",
    )

    def _compute_has_restricted_access(self):
        res = super()._compute_has_restricted_access()
        for record in self:
            record.has_restricted_access = record.restricted_access
        return res
