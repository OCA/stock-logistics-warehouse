# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements):
        if procurements and "procure_location_id" in procurements:
            procurements["location_id"] = procurements.get("procure_location_id")
        return super(ProcurementGroup, self).run(procurements)
