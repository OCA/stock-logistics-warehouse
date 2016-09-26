# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _
import openerp.addons.decimal_precision as dp


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'

    @api.multi
    @api.constrains('quants_lines')
    def check_qty(self):
        for record in self:
            if record.quants_lines:
                move = self.env['stock.move'].browse(
                    self.env.context['active_id'])
                if record.lines_qty > move.product_uom_qty:
                    raise exceptions.Warning(
                        _('Quantity is higher than the needed one'))

    @api.depends('quants_lines', 'quants_lines.qty')
    def _compute_qties(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        lines_qty = sum(self.quants_lines.mapped('qty'))
        self.lines_qty = lines_qty
        self.move_qty = move.product_uom_qty - lines_qty

    name = fields.Char(string='Name')
    lines_qty = fields.Float(
        string='Reserved qty', compute='_compute_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    move_qty = fields.Float(string='Remaining qty', compute='_compute_qties',
                            digits=dp.get_precision('Product Unit of Measure'))
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
        self.pool['stock.picking'].do_prepare_partial(
            self.env.cr, self.env.uid, [move.picking_id.id],
            context=self.env.context)
        return {}

    @api.model
    def _prepare_quants_lines(self, move, available_quant):
        return {
            'quant': available_quant.id,
            'lot_id': available_quant.lot_id.id,
            'package_id': available_quant.package_id.id,
            'selected':  available_quant in move.reserved_quant_ids,
            'qty': available_quant.qty if
            available_quant in move.reserved_quant_ids else 0,
            'location_id': available_quant.location_id.id,
        }

    @api.model
    def default_get(self, var_fields):
        rec = super(AssignManualQuants, self).default_get(var_fields)
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        available_quants = self.env['stock.quant'].search([
            ('location_id', 'child_of', move.location_id.id),
            ('product_id', '=', move.product_id.id),
            ('qty', '>', 0),
            '|',
            ('reservation_id', '=', False),
            ('reservation_id', '=', move.id)
        ])
        quants_lines = []
        for available_quant in available_quants:
            quants_lines.append([0, 0, self._prepare_quants_lines(
                move, available_quant)])
        rec.update({'quants_lines': quants_lines})
        return rec


class AssignManualQuantsLines(models.TransientModel):
    _name = 'assign.manual.quants.lines'
    _rec_name = 'quant'

    @api.multi
    @api.onchange('selected')
    def onchange_selected(self):
        for record in self:
            if not record.selected:
                record.qty = False
            elif not record.qty:
                quant_qty = record.quant.qty
                remaining_qty = record.assign_wizard.move_qty
                record.qty = (quant_qty if quant_qty < remaining_qty else
                              remaining_qty)

    assign_wizard = fields.Many2one(
        comodel_name='assign.manual.quants', string='Move', required=True,
        ondelete='cascade')
    quant = fields.Many2one(
        comodel_name='stock.quant', string='Quant', required=True,
        ondelete='cascade')
    location_id = fields.Many2one(
        comodel_name='stock.location', string='Location',
        related='quant.location_id', readonly=True)
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Lot',
        related='quant.lot_id', readonly=True,
        groups="stock.group_production_lot")
    package_id = fields.Many2one(
        comodel_name='stock.quant.package', string='Package',
        related='quant.package_id', readonly=True,
        groups="stock.group_tracking_lot")
    qty = fields.Float(
        string='QTY', digits=dp.get_precision('Product Unit of Measure'))
    selected = fields.Boolean(string='Select')
