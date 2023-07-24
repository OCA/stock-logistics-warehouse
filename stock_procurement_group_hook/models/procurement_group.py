# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.tools import float_is_zero


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _skip_procurement(self, procurement):
        return procurement.product_id.type not in ("consu", "product") or float_is_zero(
            procurement.product_qty, precision_rounding=procurement.product_uom.rounding
        )
