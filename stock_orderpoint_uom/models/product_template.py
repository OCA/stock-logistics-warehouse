# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('uom_id')
    def _check_orderpoint_procure_uom(self):
        for rec in self:
            orderpoint = self.env['stock.warehouse.orderpoint'].search([
                ('procure_uom_id.category_id', '!=',
                 rec.uom_id.category_id.id),
                ('product_id', 'in', rec.product_variant_ids.ids)], limit=1)
            if orderpoint:
                raise UserError(
                    _("At least one reordering rule for this product has a "
                      "different Procurement unit of measure category."))
