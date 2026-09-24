# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "restricted.access.mixin"]

    def _compute_has_restricted_access(self):
        res = super()._compute_has_restricted_access()
        for record in self:
            record.has_restricted_access = record.categ_id.restricted_access
        return res
