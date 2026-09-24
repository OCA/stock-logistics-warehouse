# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse", "restricted.access.mixin"]

    restricted_access = fields.Boolean(
        help="If checked, only users with restricted access can modify this record",
    )

    def _compute_has_restricted_access(self):
        res = super()._compute_has_restricted_access()
        for record in self:
            record.has_restricted_access = record.restricted_access
        return res
