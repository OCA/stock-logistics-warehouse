# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = ["stock.location", "restricted.access.mixin"]

    def _compute_has_restricted_access(self):
        res = super()._compute_has_restricted_access()
        for record in self:
            record.has_restricted_access = record.warehouse_id.restricted_access
        return res
