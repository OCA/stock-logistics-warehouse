# Copyright 2015 Mikel Arregi - AvanzOSC
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class AssignManualQuants(models.TransientModel):
    _name = 'assign.manual.quants'

    @api.multi
    @api.constrains('quants_lines')
    def _check_qty(self):
        precision_digits = self.env[
            'decimal.precision'].precision_get('Product Unit of Measure')
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        for record in self.filtered('quants_lines'):
            if float_compare(record.lines_qty, move.product_qty,
                             precision_digits=precision_digits) > 0:
                raise UserError(
                    _('Quantity is higher than the needed one'))

    @api.depends('quants_lines', 'quants_lines.qty')
    def _compute_qties(self):
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        lines_qty = sum(quant_line.qty for quant_line in self.quants_lines
                        if quant_line.selected)
        self.lines_qty = lines_qty
        self.move_qty = move.product_qty - lines_qty

    lines_qty = fields.Float(
        string='Reserved qty', compute='_compute_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    move_qty = fields.Float(string='Remaining qty', compute='_compute_qties',
                            digits=dp.get_precision('Product Unit of Measure'))
    quants_lines = fields.One2many('assign.manual.quants.lines',
                                   'assign_wizard', string='Quants')
    move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Move',
    )

    @api.multi
    def assign_quants(self):
        quant = self.env['stock.quant']
        move = self.move_id
        move._do_unreserve()
        precision_digits = self.env[
            'decimal.precision'].precision_get('Product Unit of Measure')
        for line in self.quants_lines:
            if float_compare(line.qty, 0.0,
                             precision_digits=precision_digits) > 0:
                available_quantity = quant._get_available_quantity(
                    move.product_id,
                    line.location_id,
                    lot_id=line.lot_id)
                if float_compare(available_quantity, 0.0,
                                 precision_digits=precision_digits) <= 0:
                    continue
                move._update_reserved_quantity(line.qty, available_quantity,
                                               line.location_id,
                                               lot_id=line.lot_id, strict=True)

        if move.has_move_lines:
            for ml in move.move_line_ids:
                ml.qty_done = ml.product_qty
        move._recompute_state()
        move.mapped('picking_id')._compute_state()
        return {}

    @api.model
    def default_get(self, fields):
        res = super(AssignManualQuants, self).default_get(fields)
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        available_quants = self.env['stock.quant'].search([
            ('location_id', 'child_of', move.location_id.id),
            ('product_id', '=', move.product_id.id),
            ('quantity', '>', 0)
        ])
        quants_lines = []
        for quant in available_quants:
            line = {}
            line['quant'] = quant.id
            line['lot_id'] = quant.lot_id.id
            line['on_hand'] = quant.quantity
            line['in_date'] = quant.in_date
            line['package_id'] = quant.package_id.id
            line['selected'] = False
            line['qty'] = 0
            move_lines = move.move_line_ids.filtered(
                lambda ml:
                ml.location_id == quant.location_id and
                ml.lot_id == quant.lot_id)
            for ml in move_lines:
                line['qty'] = line['qty'] + ml.ordered_qty
                line['selected'] = True
            line['reserved'] = quant.reserved_quantity - line['qty']
            line['location_id'] = quant.location_id.id
            quants_lines.append(line)
        res.update({'quants_lines': quants_lines, 'move_id': move.id})
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
                quant = record.quant
                quant_qty = quant.quantity - quant.reserved_quantity
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
    on_hand = fields.Float(
        string='On Hand', digits=dp.get_precision('Product Unit of Measure'))
    reserved = fields.Float(
        string='Others Reserved',
        digits=dp.get_precision('Product Unit of Measure'))
    selected = fields.Boolean(string='Select')
    qty = fields.Float(
        string='QTY', digits=dp.get_precision('Product Unit of Measure'))
