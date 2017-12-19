# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def action_traceability_operation(self):
        """Return an action directing to the traceability report"""
        variants = self.mapped('product_variant_ids')
        return variants.action_traceability_operation()
