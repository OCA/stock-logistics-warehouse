# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, exceptions, fields, models
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'

    @api.multi
    @api.constrains('quants_lines')
    def check_qty(self):
        precision_digits = self.env[
            'decimal.precision'].precision_get('Product Unit of Measure')
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        for record in self.filtered('quants_lines'):
            if float_compare(record.lines_qty, move.product_qty,
                             precision_digits=precision_digits) > 0:
                raise exceptions.UserError(
                    _('Quantity is higher than the needed one'))

    @api.depends('quants_lines', 'quants_lines.qty')
    def _compute_qties(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])

        lines_qty = sum(quant_line.qty for quant_line in self.quants_lines
                        if quant_line.selected)
        self.lines_qty = lines_qty
        self.move_qty = move.product_qty - lines_qty

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
        # Mark as recompute pack needed
        if move.picking_id:  # pragma: no cover
            move.picking_id.recompute_pack_op = True
        for quant_id in move.reserved_quant_ids.ids:
            move.write({'reserved_quant_ids': [[3, quant_id]]})
        for line in self.quants_lines.filtered('selected'):
            quants.append([line.quant, line.qty])
        self.env['stock.quant'].quants_reserve(quants, move)
        return {}

    @api.model
    def default_get(self, fields):
        res = super(AssignManualQuants, self).default_get(fields)
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        available_quants = self.env['stock.quant'].search([
            ('location_id', 'child_of', move.location_id.id),
            ('product_id', '=', move.product_id.id),
            ('qty', '>', 0),
            '|',
            ('reservation_id', '=', False),
            ('reservation_id', '=', move.id)
        ])
        quants_lines = [{
            'quant': x.id,
            'lot_id': x.lot_id.id,
            'in_date': x.in_date,
            'package_id': x.package_id.id,
            'selected': x in move.reserved_quant_ids,
            'qty': x.qty if x in move.reserved_quant_ids else 0,
            'location_id': x.location_id.id,
        } for x in available_quants]
        res.update({'quants_lines': quants_lines})
        res = self._convert_to_write(self._convert_to_cache(res))
        return res


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
    in_date = fields.Date(
        string='Incoming Date', readonly=True)
    package_id = fields.Many2one(
        comodel_name='stock.quant.package', string='Package',
        related='quant.package_id', readonly=True,
        groups="stock.group_tracking_lot")
    qty = fields.Float(
        string='QTY', digits=dp.get_precision('Product Unit of Measure'))
    selected = fields.Boolean(string='Select')
