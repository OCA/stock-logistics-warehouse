# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from random import randint

from odoo import _, api, exceptions, fields, models


class StockKardex(models.Model):
    _name = 'stock.kardex'
    _inherit = 'barcodes.barcode_events_mixin'
    _description = 'Stock Kardex'

    name = fields.Char()
    address = fields.Char()
    mode = fields.Selection(
        [('pick', 'Pick'), ('put', 'Put'), ('inventory', 'Inventory')],
        default='pick',
        required=True,
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        required=True,
        domain="[('kardex', '=', True)]",
        context="{'default_kardex': True}",
        ondelete='restrict',
        help="The Kardex source location for Pick operations "
        "and destination location for Put operations.",
    )
    current_move_line = fields.Many2one(comodel_name='stock.move.line')

    operation_descr = fields.Char(
        string="Operation", default="Scan next PID", readonly=True
    )

    # tray information (will come from stock.location or a new tray model)
    kardex_tray_x = fields.Integer(
        string='X', compute='_compute_kardex_tray_matrix'
    )
    kardex_tray_y = fields.Integer(
        string='Y', compute='_compute_kardex_tray_matrix'
    )
    kardex_tray_matrix = fields.Serialized(
        compute='_compute_kardex_tray_matrix'
    )

    # current operation information
    picking_id = fields.Many2one(
        related='current_move_line.picking_id', readonly=True
    )
    product_id = fields.Many2one(
        related='current_move_line.product_id', readonly=True
    )
    product_uom_id = fields.Many2one(
        related='current_move_line.product_uom_id', readonly=True
    )
    product_uom_qty = fields.Float(
        related='current_move_line.product_uom_qty', readonly=True
    )
    qty_done = fields.Float(
        related='current_move_line.qty_done', readonly=True
    )
    lot_id = fields.Many2one(related='current_move_line.lot_id', readonly=True)

    _barcode_scanned = fields.Char(
        "Barcode Scanned",
        help="Value of the last barcode scanned.",
        store=False,
    )

    def on_barcode_scanned(self, barcode):
        raise exceptions.UserError('Scanned barcode: {}'.format(barcode))

    @api.depends()
    def _compute_kardex_tray_matrix(self):
        for record in self:
            # prototype code, random matrix
            cols = randint(4, 8)
            rows = randint(1, 3)
            selected = [randint(0, cols - 1), randint(0, rows - 1)]
            cells = []
            for __ in range(rows):
                row = []
                for __ in range(cols):
                    row.append(randint(0, 1))
                cells.append(row)

            record.kardex_tray_x = selected[0] + 1
            record.kardex_tray_y = selected[1] + 1
            record.kardex_tray_matrix = {
                # x, y: position of the selected cell
                'selected': selected,
                # 0 is empty, 1 is not
                'cells': cells,
            }

    def action_open_screen(self):
        self.ensure_one()
        screen_xmlid = 'stock_kardex.stock_kardex_view_form_screen'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'views': [[self.env.ref(screen_xmlid).id, 'form']],
            'res_id': self.id,
            'target': 'fullscreen',
            'flags': {
                'headless': True,
                'form_view_initial_mode': 'edit',
                'no_breadcrumbs': True,
            },
        }

    def action_menu(self):
        menu_xmlid = 'stock_kardex.stock_kardex_form_menu'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.kardex',
            'views': [[self.env.ref(menu_xmlid).id, 'form']],
            'name': _('Menu'),
            'target': 'new',
            'res_id': self.id,
        }

    def action_quit_screen(self):
        action_xmlid = 'stock_kardex.stock_kardex_action'
        return self.env.ref(action_xmlid).read()[0]

    # TODO: should the mode be changed on all the kardex at the same time?
    def switch_pick(self):
        self.mode = 'pick'

    def switch_put(self):
        self.mode = 'put'

    def switch_inventory(self):
        self.mode = 'inventory'
