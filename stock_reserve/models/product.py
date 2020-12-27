from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    reservation_count = fields.Float(
        compute='_compute_reservation_count',
        string='# Sales')

    @api.multi
    def _compute_reservation_count(self):
        for product in self:
            product.reservation_count = sum(
                product.product_variant_ids.mapped('reservation_count'))

    @api.multi
    def action_view_reservations(self):
        self.ensure_one()
        ref = 'stock_reserve.action_stock_reservation_tree'
        product_ids = self.mapped('product_variant_ids.id')
        action_dict = self.env.ref(ref).read()[0]
        action_dict['domain'] = [('product_id', 'in', product_ids)]
        action_dict['context'] = {
            'search_default_draft': 1,
            'search_default_reserved': 1
            }
        return action_dict


class ProductProduct(models.Model):
    _inherit = 'product.product'

    reservation_count = fields.Float(
        compute='_compute_reservation_count',
        string='# Sales')

    @api.multi
    def _compute_reservation_count(self):
        for product in self:
            domain = [('product_id', '=', product.id),
                      ('state', 'in', ['draft', 'assigned'])]
            reservations = self.env['stock.reservation'].search(domain)
            product.reservation_count = sum(reservations.mapped('product_qty'))

    @api.multi
    def action_view_reservations(self):
        self.ensure_one()
        ref = 'stock_reserve.action_stock_reservation_tree'
        action_dict = self.env.ref(ref).read()[0]
        action_dict['domain'] = [('product_id', '=', self.id)]
        action_dict['context'] = {
            'search_default_draft': 1,
            'search_default_reserved': 1
            }
        return action_dict
