# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class BoM(models.Model):
    _inherit = "mrp.bom"

    def get_produced_items(self):
        """
        Returns the Products Variants produced by a BoM
        """
        variants = self.product_id

        template_boms = self.filtered(lambda x: not x.product_id)
        templates = template_boms.product_tmpl_id
        template_variants = templates.product_variant_ids
        return variants | template_variants

class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        res = super(ReportBomStructure, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        res['proposed_cost'] = res['product'].proposed_cost
        return res

    @api.model
    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        res = super(ReportBomStructure, self)._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        for line in res[0]:
            product_id = self.env["product.product"].browse([line['prod_id']])
            line['proposed_cost'] = product_id.proposed_cost
        
        return res