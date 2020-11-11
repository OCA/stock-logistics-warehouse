# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
    ):
        if values and "procure_location_id" in values:
            location_id = values.get("procure_location_id")
        return super(ProcurementGroup, self).run(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            values,
        )
