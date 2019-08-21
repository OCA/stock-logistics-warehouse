# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class StockMoveLineSerialGenerator(models.TransientModel):

    _name = 'stock.move.line.serial.generator'
    _description = 'Auto generate serial numbers'

    stock_move_id = fields.Many2one('stock.move', readonly=True)
    product_id = fields.Many2one(
        'product.product', related='stock_move_id.product_id'
    )
    picking_type_create_lots = fields.Boolean(
        related='stock_move_id.picking_type_create_lots'
    )
    qty_to_process = fields.Integer(
        help="Defines how many serial numbers will be generated on stock move "
        "lines without a serial number yet."
    )
    first_number = fields.Char(required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        stock_move_id = self.env.context.get('active_id')
        move = self.env['stock.move'].browse(stock_move_id)
        if 'qty_to_process' in fields:
            lines_without_serial = move.move_line_ids.filtered(
                lambda m: not m.lot_name
            )
            res['qty_to_process'] = len(lines_without_serial)
        return res

    @api.multi
    def _check_new_serials_usage(self, serials_list):
        """Check if a generated number is already used on existing
        stock.production.lot or stock.move.line."""
        errors = []
        lots = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('name', 'in', serials_list)
        ])
        sm_lines = self.env['stock.move.line'].search([
            ('product_id', '=', self.product_id.id),
            ('lot_name', 'in', serials_list)
        ])
        if self.picking_type_create_lots:
            if lots:
                errors += lots.mapped('name')
            if sm_lines:
                errors += sm_lines.mapped('lot_name')
        else:
            if not lots:
                errors += serials_list
        if errors and self.picking_type_create_lots:
            raise ValidationError(
                _('The following serial numbers are already in use:\n%s')
                % '\n'.join(set(errors))
            )
        elif errors:
            raise ValidationError(
                _("The following serial numbers don't exist:\n%s")
                % '\n'.join(errors)
            )
        return True

    @api.constrains('qty_to_process')
    def _check_qty_to_process(self):
        """Ensure the user doesn't enter a higher number as available lines"""
        self.ensure_one()
        available_lines = self.stock_move_id.move_line_ids.filtered(
            lambda l: not l.lot_name
        )
        max_qty = sum(available_lines.mapped('product_uom_qty'))
        if self.qty_to_process > max_qty:
            raise ValidationError(
                _(
                    "The qty received cannot exceed the number of"
                    " move lines not having a serial number yet. (%s)"
                )
                % max_qty
            )

    @api.multi
    def generate_serials(self):
        """Generate serial numbers and update stock.move.line if available"""
        self.ensure_one()
        move_lines = self.stock_move_id.move_line_ids.filtered(
            lambda l: not l.lot_name and not l.lot_id
        )
        new_serials = self._get_new_serials()
        self._check_new_serials_usage(new_serials)
        if self.picking_type_create_lots:
            self._fill_with_new_serials(move_lines, new_serials)
        else:
            self._fill_with_existing_serials(move_lines, new_serials)
        return self.stock_move_id.action_show_details()

    def _get_new_serials(self):
        """If needed 'ir.sequence' can be used
         we expect only the simple number"""
        if not self.first_number.isdigit():
            raise ValidationError(_('Only numbers are allowed'))
        number = int(self.first_number)
        return [i for i in range(number, self.qty_to_process + number)]

    def _fill_with_new_serials(self, move_lines, new_serials):
        for i in range(self.qty_to_process):
            move_line = move_lines[i]
            move_line.update({'lot_name': new_serials[i]})
            move_line.onchange_serial_number()

    def _fill_with_existing_serials(self, move_lines, new_serials):
        serials = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('name', 'in', new_serials),
        ])
        if len(serials) != self.qty_to_process:
            raise UserError(
                _(
                    'Quantity to process is not equal to quantity of '
                    'generated serial numbers'
                )
            )
        for i in range(self.qty_to_process):
            move_line = move_lines[i]
            move_line.update({'lot_id': serials[i]})
            move_line.onchange_serial_number()

    def cancel(self):
        return self.stock_move_id.action_show_details()
