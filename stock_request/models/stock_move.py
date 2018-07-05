# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    allocation_ids = fields.One2many(comodel_name='stock.request.allocation',
                                     inverse_name='stock_move_id',
                                     string='Stock Request Allocation')

    stock_request_ids = fields.One2many(comodel_name='stock.request',
                                        string='Stock Requests',
                                        compute='_compute_stock_request_ids')

    @api.depends('allocation_ids')
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.allocation_ids.mapped(
                'stock_request_id')

    def _merge_moves_fields(self):
        res = super(StockMove, self)._merge_moves_fields()
        res['allocation_ids'] = [(4, m.id) for m in
                                 self.mapped('allocation_ids')]
        return res

    @api.constrains('company_id')
    def _check_company_stock_request(self):
        if any(self.env['stock.request.allocation'].search(
                [('company_id', '!=', rec.company_id.id),
                 ('stock_move_id', '=', rec.id)], limit=1)
               for rec in self):
            raise ValidationError(
                _('The company of the stock request must match with '
                  'that of the location.'))

    @api.model
    def _stock_request_confirm_done_message_content(self, message_data):
        title = _('Receipt confirmation %s for your Request %s') % (
            message_data['picking_name'], message_data['request_name'])
        message = '<h3>%s</h3>' % title
        message += _('The following requested items from Stock Request %s '
                     'have now been received in %s using Picking %s:') % (
            message_data['request_name'], message_data['location_name'],
            message_data['picking_name'])
        message += '<ul>'
        message += _(
            '<li><b>%s</b>: Transferred quantity %s %s</li>'
        ) % (message_data['product_name'],
             message_data['product_qty'],
             message_data['product_uom'],
             )
        message += '</ul>'
        return message

    def _prepare_message_data(self, move, request, allocated_qty):
        return {
            'request_name': request.name,
            'picking_name': move.picking_id.name,
            'product_name': move.product_id.name_get()[0][1],
            'product_qty': allocated_qty,
            'product_uom': move.product_uom.name,
            'location_name': move.location_dest_id.name_get()[0][1],
        }

    @api.multi
    def action_done(self):
        for move in self:
            qty_done = move.product_uom._compute_quantity(
                move.product_uom_qty, move.product_id.uom_id)
            to_allocate_qty = move.product_uom_qty
            for allocation in move.allocation_ids.sudo():
                allocated_qty = 0.0
                if allocation.open_product_qty:
                    allocated_qty = min(
                        allocation.open_product_qty, qty_done)
                    allocation.allocated_product_qty += allocated_qty
                    to_allocate_qty -= allocated_qty
                request = allocation.stock_request_id
                message_data = self._prepare_message_data(move, request,
                                                          allocated_qty)
                message = \
                    self._stock_request_confirm_done_message_content(
                        message_data)
                request.message_post(body=message, subtype='mail.mt_comment')
                request.check_done()
        super(StockMove, self).action_done()
        return True
