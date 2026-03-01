from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self):
        res = super(StockMove, self)._action_done()
        # In Odoo 12, _action_done returns the done moves. We also check self.
        done_moves = res if isinstance(res, models.Model) else self
        products = done_moves.mapped('product_id')
        if products:
            # We use sudo() because an internal transfer might update quantities
            # but the user running it might not have rights to update product.product
            products.sudo()._update_available_warehouses()
            products.sudo()._update_available_locations()
        return res

    def _update_all_products(self):
        prod_s = self.env['product.product'].search([('qty_available', '>', 0)])
        for prod in prod_s:
            # We use sudo() because an internal transfer might update quantities
            # but the user running it might not have rights to update product.product
            prod.sudo()._update_available_warehouses()
            prod.sudo()._update_available_locations()
