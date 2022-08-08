# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        procure_location = values.get("procure_location_id", False)
        if procure_location:
            location_id = procure_location
        return super()._get_rule(product_id, location_id, values)
