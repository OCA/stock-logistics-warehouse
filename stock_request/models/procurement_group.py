# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements):
        indexes_to_pop = []
        new_procs = []
        for i, procurement in enumerate(procurements):
            if "stock_request_id" in procurement.values and procurement.values.get(
                "stock_request_id"
            ):
                req = self.env["stock.request"].browse(
                    procurement.values.get("stock_request_id")
                )
                if req.order_id:
                    new_procs.append(procurement._replace(origin=req.order_id.name))
                    indexes_to_pop.append(i)
        if new_procs:
            indexes_to_pop.reverse()
            for index in indexes_to_pop:
                procurements.pop(index)
            procurements.extend(new_procs)
        return super().run(procurements)
