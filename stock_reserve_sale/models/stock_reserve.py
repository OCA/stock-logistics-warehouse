from odoo import models, fields, api


class StockReservation(models.Model):
    _inherit = 'stock.reservation'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        ondelete='cascade',
        copy=False)
    sale_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        related='sale_line_id.order_id')

    @api.multi
    def release(self):
        self.write({'sale_line_id': False})
        return super(StockReservation, self).release()
