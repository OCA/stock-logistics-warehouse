# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


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
