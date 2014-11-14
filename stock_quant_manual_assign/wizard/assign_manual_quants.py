
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import fields, models, api, exceptions, _


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'

    @api.one
    @api.constrains('quants_lines')
    def check_qty(self):
        total_qty = 0
        for line in self.quants_lines:
            if line.selected:
                total_qty += line.qty
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        if total_qty > move.product_uom_qty:
            raise exceptions.Warning(_('Error'),
                                     _('Quantity is higher'
                                       ' than the needed one'))

    name = fields.Char(string='Name')
    quants_lines = fields.One2many('assign.manual.quants.lines',
                                   'assign_wizard', string='Quants')

    @api.multi
    def assign_quants(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        quants = []
        for quant_id in move.reserved_quant_ids.ids:
            move.write({'reserved_quant_ids': [[3, quant_id]]})
        for line in self.quants_lines:
            if line.selected:
                quants.append([line.quant, line.qty])
        self.pool['stock.quant'].quants_reserve(
            self.env.cr, self.env.uid, quants, move, context=self.env.context)
        return {}

    def default_get(self, cr, uid, var_fields, context=None):
        move = self.pool['stock.move'].browse(
            cr, uid, context['active_id'], context=context)
        available_quants_ids = self.pool['stock.quant'].search(
            cr, uid, [
                '|', ('location_id', '=', move.location_id.id),
                ('location_id', 'in', move.location_id.child_ids.ids),
                ('product_id', '=', move.product_id.id),
                ('qty', '>', 0),
                ('reservation_id', '=', False)], context=context)
        available_quants = [{'quant': x} for x in available_quants_ids]
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

    assign_wizard = fields.Many2one('assign.manual.quants', string='Move',
                                    required=True)
    quant = fields.Many2one('stock.quant', string="Quant", required=True)
    qty = fields.Float(string='QTY')
    selected = fields.Boolean(string="Select")
