# Copyright 2020 Matt Taylor
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockInventoryRevaluationGetMoves(models.TransientModel):

    _name = 'stock.inventory.revaluation.get.moves'
    _description = 'Inventory revaluation get moves'

    revaluation_id = fields.Many2one(
        comodel_name='stock.inventory.revaluation',
        string='Revaluation',
        required=True)

    product_id = fields.Many2one(
        comodel_name='product.product',
        related='revaluation_id.product_id')

    date_from = fields.Date('Date From')

    date_to = fields.Date('Date To')

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial',
        domain="[('product_id', '=', product_id)]")

    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        domain=[('usage', '=', 'internal')])

    @api.model
    def default_get(self, fields):
        res = super(StockInventoryRevaluationGetMoves, self).default_get(
            fields)
        reval_id = self.env.context.get('active_id')
        if reval_id:
            res['revaluation_id'] = reval_id
        return res

    def _get_move_search_criteria(self):
        domain = [
            ('state', '=', 'done'),
            ('product_id', '=', self.product_id.id),
            ('remaining_qty', '>', 0.0),
        ]
        if self.location_id:
            domain.extend([('location_dest_id', '=', self.location_id.id)])
        else:
            domain.extend([('location_dest_id.usage', '=', 'internal')])
        if self.date_from:
            domain.extend([('date', '>=', self.date_from)])
        if self.date_to:
            domain.extend([('date', '<=', self.date_to)])
        if self.lot_id:
            line_domain = [('lot_id', '=', self.lot_id.id)]
            move_line_ids = self.env['stock.move.line'].search(line_domain)
            domain.extend([('id', 'in', move_line_ids.mapped('move_id').ids)])
        return domain

    def _prepare_line_move_data(self, move):
        return {
            'revaluation_id': self.revaluation_id.id,
            'move_id': move.id,
            'new_value': move.remaining_value,
        }

    @api.multi
    def process(self):
        self.ensure_one()
        reval_move_obj = self.env['stock.inventory.revaluation.move']

        # Delete the previous records
        self.revaluation_id.reval_move_ids.unlink()

        moves = self.env['stock.move'].search(self._get_move_search_criteria())
        for move in moves:
            m_data = self._prepare_line_move_data(move)
            reval_move_obj.create(m_data)

        return {'type': 'ir.actions.act_window_close'}
