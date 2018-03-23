# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.multi
    def write(self, values):
        if values.get('property_cost_method', False):
            products_to_upd = self.env['product.template'].search([
                ('categ_id', '=', self.ids)])
            products_to_upd.write({
                'cost_method': values.get('property_cost_method')})
        return super(ProductCategory, self).write(values)
