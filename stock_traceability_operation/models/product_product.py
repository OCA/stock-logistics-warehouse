# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def action_traceability_operation(self):
        """Return an action on the report"""
        quants = self.env['stock.quant'].search(
            [('product_id', 'in', self.ids)])
        return quants.action_traceability_operation()
