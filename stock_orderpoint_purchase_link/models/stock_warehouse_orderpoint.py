# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import ast

from odoo import fields, models
from odoo.osv.expression import OR


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    purchase_line_ids = fields.Many2many(
        comodel_name='purchase.order.line',
        string='Purchase Order Lines', copy=False,
        readonly=True,
    )

    def action_view_purchase(self):
        """ This function returns an action that display existing
        purchase orders of given orderpoint.
        """
        result = super(StockWarehouseOrderpoint, self).action_view_purchase()
        if self.purchase_line_ids:
            order_ids = self.purchase_line_ids.mapped('order_id')
            result['domain'] = OR([ast.literal_eval(result['domain']),
                                   ast.literal_eval(
                                       "[('id','in',%s)]" % order_ids.ids)])

        return result
