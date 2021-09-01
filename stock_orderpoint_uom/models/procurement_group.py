# Copyright (C) 2018 - TODAY, Open Source Integrators
# (http://www.opensourceintegrators.com)
# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        # 'Procurement' is a 'namedtuple', which is not editable.
        # The 'procurement' which needs to be edited is created new
        # and the previous one is deleted.
        Proc = self.env["procurement.group"].Procurement
        indexes_to_pop = []
        new_procs = []
        for i, procurement in enumerate(procurements):
            if "orderpoint_id" in procurement.values:
                orderpoint = procurement.values.get("orderpoint_id")
                if (
                    orderpoint.procure_uom_id
                    and procurement.product_uom != orderpoint.procure_uom_id
                ):
                    new_product_qty = procurement.product_uom._compute_quantity(
                        procurement.product_qty, orderpoint.procure_uom_id
                    )
                    new_product_uom = orderpoint.procure_uom_id
                    new_procs.append(
                        Proc(
                            procurement.product_id,
                            new_product_qty,
                            new_product_uom,
                            procurement.location_id,
                            procurement.name,
                            procurement.origin,
                            procurement.company_id,
                            procurement.values,
                        )
                    )
                    indexes_to_pop.append(i)
        if new_procs:
            indexes_to_pop.reverse()
            for index in indexes_to_pop:
                procurements.pop(index)
        procurements.extend(new_procs)
        return super(ProcurementGroup, self).run(procurements, raise_user_error)
