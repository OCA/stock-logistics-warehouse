# Copyright 2021-2022 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        # Store the reorder source Procurement Groups
        # To be used for reference and link navigation
        # Also updates the Origin field of the PO
        Forecast = self.env["report.stock.report_product_product_replenishment"]
        new_procurements = []
        for procurement in procurements:
            product = procurement.product_id
            # TODO: set warehouse_id in context?
            data = Forecast._get_report_data(product_variant_ids=[product.id])
            source_docs = set()  # Avoid duplicate sources
            for line in data["lines"]:
                if not line["document_in"] and line["document_out"]:
                    source_docs.add(line["document_out"])
            if source_docs:
                source_groups = [x.procurement_group_id for x in source_docs]
                source_names = ", ".join([x.name for x in source_docs])
                new_origin = "%s (from %s)" % (source_names, procurement.origin)
                new_procurement = procurement._replace(origin=new_origin)
                new_procurement.values["source_group_ids"] = source_groups
                new_procurements.append(new_procurement)
            else:
                new_procurements.append(procurement)
        return super().run(new_procurements, raise_user_error=True)
