# Copyright 2015 Mikel Arregi - AvanzOSC
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Fanha Giang
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
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
        for record in self.filtered('quants_lines'):
            if float_compare(record.lines_qty, record.move_id.product_qty,
                             precision_digits=precision_digits) > 0:
                raise UserError(
                    _('Quantity is higher than the needed one'))

    @api.depends('move_id', 'quants_lines', 'quants_lines.qty')
    def _compute_qties(self):
        for record in self:
            record.lines_qty = sum(
                record.quants_lines.filtered('selected').mapped('qty')
            )
            record.move_qty = record.move_id.product_qty - record.lines_qty

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
            ('quantity', '>', 0),
        ])
        quants_lines = []
        for quant in available_quants:
            line = {}
            line['quant_id'] = quant.id
            line['on_hand'] = quant.quantity
            line['location_id'] = quant.location_id.id
            line['lot_id'] = quant.lot_id.id
            line['package_id'] = quant.package_id.id
            line['selected'] = False
            move_lines = move.move_line_ids.filtered(
                lambda ml: (ml.location_id == quant.location_id and
                            ml.lot_id == quant.lot_id)
            )
            line['qty'] = sum(move_lines.mapped('ordered_qty'))
            line['selected'] = bool(line['qty'])
            line['reserved'] = quant.reserved_quantity - line['qty']
            quants_lines.append(line)
        res.update({
            'quants_lines': [(0, 0, x) for x in quants_lines],
            'move_id': move.id,
        })
        return res


class AssignManualQuantsLines(models.TransientModel):
    _name = 'assign.manual.quants.lines'
    _rec_name = 'quant_id'

    assign_wizard = fields.Many2one(
        comodel_name='assign.manual.quants', string='Move', required=True,
        ondelete='cascade')
    quant_id = fields.Many2one(
        comodel_name='stock.quant', string='Quant', required=True,
        ondelete='cascade', oldname='quant')
    location_id = fields.Many2one(
        comodel_name='stock.location', string='Location',
        related='quant_id.location_id', readonly=True)
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Lot',
        related='quant_id.lot_id', readonly=True,
        groups="stock.group_production_lot")
    package_id = fields.Many2one(
        comodel_name='stock.quant.package', string='Package',
        related='quant_id.package_id', readonly=True,
        groups="stock.group_tracking_lot")
    # This is not correctly shown as related or computed, so we make it regular
    on_hand = fields.Float(
        readonly=True,
        string='On Hand',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    reserved = fields.Float(
        string='Others Reserved',
        digits=dp.get_precision('Product Unit of Measure'))
    selected = fields.Boolean(string='Select')
    qty = fields.Float(
        string='QTY', digits=dp.get_precision('Product Unit of Measure'))

    @api.onchange('selected')
    def _onchange_selected(self):
        for record in self:
            if not record.selected:
                record.qty = 0
            elif not record.qty:
                # This takes current "snapshot" situation, so that we don't
                # have to compute each time if current reserved quantity is
                # for this current move. If other operations change available
                # quantity on quant, a constraint would be raised later on
                # validation.
                quant_qty = record.on_hand - record.reserved
                remaining_qty = record.assign_wizard.move_qty
                record.qty = min(quant_qty, remaining_qty)

    @api.multi
    @api.constrains('qty')
    def _check_qty(self):
        precision_digits = self.env[
            'decimal.precision'
        ].precision_get('Product Unit of Measure')
        for record in self.filtered('qty'):
            quant = record.quant_id
            move_lines = record.assign_wizard.move_id.move_line_ids.filtered(
                lambda ml: (ml.location_id == quant.location_id and
                            ml.lot_id == quant.lot_id)
            )
            reserved = (
                quant.reserved_quantity - sum(move_lines.mapped('ordered_qty'))
            )
            if float_compare(record.qty, record.quant_id.quantity - reserved,
                             precision_digits=precision_digits) > 0:
                raise UserError(
                    _('Selected line quantity is higher than the available '
                      'one. Maybe an operation with this product has been '
                      'done meanwhile or you have manually increased the '
                      'suggested value.')
                )
