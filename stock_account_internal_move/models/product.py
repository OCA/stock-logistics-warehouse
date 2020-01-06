from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _prepare_internal_svl_vals(self, quantity, unit_cost):
        self.ensure_one()
        vals = {
            'product_id': self.id,
            'value': unit_cost * quantity,
            'unit_cost': unit_cost,
            'quantity': quantity,
        }
        if self.cost_method in ('average', 'fifo'):
            vals['remaining_qty'] = quantity
            vals['remaining_value'] = vals['value']
        return vals