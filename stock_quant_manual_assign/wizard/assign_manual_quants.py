# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, exceptions, _


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'

    def lines_qty(self):
        total_qty = 0
        for line in self.quants_lines:
            if line.selected:
                total_qty += line.qty
        return total_qty

    @api.one
    @api.constrains('quants_lines')
    def check_qty(self):
        if self.quants_lines:
            total_qty = self.lines_qty()
            move = self.env['stock.move'].browse(self.env.context['active_id'])
            if total_qty > move.product_uom_qty:
                raise exceptions.Warning(_('Error'),
                                         _('Quantity is higher'
                                           ' than the needed one'))

    @api.depends('quants_lines')
    def get_move_qty(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        self.move_qty = move.product_uom_qty - self.lines_qty()

    name = fields.Char(string='Name')
    move_qty = fields.Float(string="Remaining qty", compute="get_move_qty")
    quants_lines = fields.One2many('assign.manual.quants.lines',
                                   'assign_wizard', string='Quants')

    @api.multi
    def assign_quants(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        move.picking_id.mapped('pack_operation_ids').unlink()
        quants = []
        for quant_id in move.reserved_quant_ids.ids:
            move.write({'reserved_quant_ids': [[3, quant_id]]})
        for line in self.quants_lines:
            if line.selected:
                quants.append([line.quant, line.qty])
        self.pool['stock.quant'].quants_reserve(
            self.env.cr, self.env.uid, quants, move, context=self.env.context)
        return {}

    @api.model
    def default_get(self, var_fields):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        available_quants_ids = self.env['stock.quant'].search(
            ['|', ('location_id', '=', move.location_id.id),
             ('location_id', 'in', move.location_id.child_ids.ids),
             ('product_id', '=', move.product_id.id),
             ('qty', '>', 0),
             ('reservation_id', '=', False)])
        available_quants = [{'quant': x.id} for x in available_quants_ids]
        available_quants.extend(
            {'quant': x.id,
             'selected': True,
             'qty': x.qty
             } for x in move.reserved_quant_ids)
        return {'quants_lines': available_quants}


class AssignManualQuantsLines(models.TransientModel):
    _name = 'assign.manual.quants.lines'
    _rec_name = 'quant'

    @api.onchange('selected')
    def onchange_selected(self):
            if not self.selected:
                self.qty = False
            if self.selected and self.qty == 0:
                quant_qty = self.quant.qty
                remaining_qty = self.assign_wizard.move_qty
                if quant_qty < remaining_qty:
                    self.qty = quant_qty
                else:
                    self.qty = remaining_qty

    assign_wizard = fields.Many2one('assign.manual.quants', string='Move',
                                    required=True, ondelete="cascade")
    quant = fields.Many2one('stock.quant', string="Quant", required=True,
                            ondelete='cascade')
    qty = fields.Float(string='QTY')
    selected = fields.Boolean(string="Select")
