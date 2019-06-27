# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_assign(self):
        # This is to assure that stock.pack.operation are reprocessed
        self.mapped('pack_operation_ids').unlink()
        return super(StockPicking, self).action_assign()


class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_type_code = fields.Selection(
        related='picking_type_id.code', store=True, readonly=True)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_unreserve(self, move):
        param = self.env['stock.config.settings']._get_parameter(
            'stock.backorder.manual_quants', False)
        if param and param.value != 'False':
            related_moves = self.env['stock.move'].search([
                ('split_from', '=', move.id)])
            related_quants = move.reserved_quant_ids
            super(StockQuant, self).quants_unreserve(move)
            related_quants.sudo().write({
                'reservation_id': related_moves[:1].id})
        else:
            super(StockQuant, self).quants_unreserve(move)
