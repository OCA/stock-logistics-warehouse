# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class VerticalLiftShuttle(models.Model):
    _name = 'vertical.lift.shuttle'
    _inherit = 'barcodes.barcode_events_mixin'
    _description = 'Vertical Lift Shuttle'

    name = fields.Char()
    mode = fields.Selection(
        [('pick', 'Pick'), ('put', 'Put'), ('inventory', 'Inventory')],
        default='pick',
        required=True,
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        required=True,
        domain="[('vertical_lift_kind', '=', 'shuttle')]",
        ondelete='restrict',
        help="The Shuttle source location for Pick operations "
        "and destination location for Put operations.",
    )
    hardware = fields.Selection(
        selection='_selection_hardware', default='simulation', required=True
    )
    current_move_line_id = fields.Many2one(comodel_name='stock.move.line')

    number_of_ops = fields.Integer(
        compute='_compute_number_of_ops', string='Number of Operations'
    )
    number_of_ops_all = fields.Integer(
        compute='_compute_number_of_ops_all',
        string='Number of Operations in all shuttles',
    )

    operation_descr = fields.Char(
        string="Operation",
        default="Scan New Destination Location",
        readonly=True,
    )

    # tray information (will come from stock.location or a new tray model)
    tray_location_id = fields.Many2one(
        comodel_name='stock.location',
        compute='_compute_tray_matrix',
        string='Tray Location',
    )
    tray_name = fields.Char(compute='_compute_tray_matrix', string='Tray Name')
    tray_type_id = fields.Many2one(
        comodel_name='stock.location.tray.type',
        compute='_compute_tray_matrix',
        string='Tray Type',
    )
    tray_type_code = fields.Char(
        compute='_compute_tray_matrix', string='Tray Code'
    )
    tray_x = fields.Integer(string='X', compute='_compute_tray_matrix')
    tray_y = fields.Integer(string='Y', compute='_compute_tray_matrix')
    tray_matrix = Serialized(string='Cells', compute='_compute_tray_matrix')
    tray_qty = fields.Float(
        string='Stock Quantity', compute='_compute_tray_qty'
    )

    # current operation information
    picking_id = fields.Many2one(
        related='current_move_line_id.picking_id', readonly=True
    )
    picking_origin = fields.Char(
        related='current_move_line_id.picking_id.origin', readonly=True
    )
    picking_partner_id = fields.Many2one(
        related='current_move_line_id.picking_id.partner_id', readonly=True
    )
    product_id = fields.Many2one(
        related='current_move_line_id.product_id', readonly=True
    )
    product_uom_id = fields.Many2one(
        related='current_move_line_id.product_uom_id', readonly=True
    )
    product_uom_qty = fields.Float(
        related='current_move_line_id.product_uom_qty', readonly=True
    )
    product_packagings = fields.Html(
        string='Packaging', compute='_compute_product_packagings'
    )
    qty_done = fields.Float(
        related='current_move_line_id.qty_done', readonly=True
    )
    lot_id = fields.Many2one(
        related='current_move_line_id.lot_id', readonly=True
    )
    location_dest_id = fields.Many2one(
        string="Destination",
        related='current_move_line_id.location_dest_id',
        readonly=True,
    )

    # TODO add a glue addon with product_expiry to add the field

    _barcode_scanned = fields.Char(
        "Barcode Scanned",
        help="Value of the last barcode scanned.",
        store=False,
    )

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        # FIXME notify_info is only for the demo
        self.env.user.notify_info('Scanned barcode: {}'.format(barcode))
        method = 'on_barcode_scanned_{}'.format(self.mode)
        getattr(self, method)(barcode)

    def on_barcode_scanned_pick(self, barcode):
        location = self.env['stock.location'].search(
            [('barcode', '=', barcode)]
        )
        if location:
            self.current_move_line_id.location_dest_id = location
            self.operation_descr = _('Save')
        else:
            self.env.user.notify_warning(
                _('No location found for barcode {}').format(barcode)
            )

    def on_barcode_scanned_put(self, barcode):
        pass

    def on_barcode_scanned_inventory(self, barcode):
        pass

    @api.model
    def _selection_hardware(self):
        return [('simulation', 'Simulation')]

    @api.depends('current_move_line_id.product_id.packaging_ids')
    def _compute_product_packagings(self):
        for record in self:
            if not record.current_move_line_id:
                continue
            product = record.current_move_line_id.product_id
            values = {
                'packagings': [
                    {
                        'name': pkg.name,
                        'qty': pkg.qty,
                        'unit': product.uom_id.name,
                    }
                    for pkg in product.packaging_ids
                ]
            }
            content = self.env['ir.qweb'].render(
                'stock_vertical_lift.packagings', values
            )
            record.product_packagings = content

    @api.depends()
    def _compute_number_of_ops(self):
        for record in self:
            record.number_of_ops = record.count_move_lines_to_do()

    @api.depends()
    def _compute_number_of_ops_all(self):
        for record in self:
            record.number_of_ops_all = record.count_move_lines_to_do_all()

    @api.depends('tray_location_id', 'current_move_line_id.product_id')
    def _compute_tray_qty(self):
        for record in self:
            if not (record.tray_location_id and record.current_move_line_id):
                continue
            product = record.current_move_line_id.product_id
            quants = self.env['stock.quant'].search(
                [
                    ('location_id', '=', record.tray_location_id.id),
                    ('product_id', '=', product.id),
                ]
            )
            record.tray_qty = sum(quants.mapped('quantity'))

    @api.depends()
    def _compute_tray_matrix(self):
        for record in self:
            modes = {
                'pick': 'location_id',
                'put': 'location_dest_id',
                # TODO what to do for inventory?
                'inventory': 'location_id',
            }
            location = record.current_move_line_id[modes[record.mode]]
            tray_type = location.location_id.tray_type_id
            selected = []
            cells = []
            if location:
                selected = location._tray_cell_coords()
                cells = location._tray_cell_matrix()

            # this is the current cell
            record.tray_location_id = location.id
            # name of the tray where the cell is
            record.tray_name = location.location_id.name
            record.tray_type_id = tray_type.id
            record.tray_type_code = tray_type.code
            record.tray_x = location.posx
            record.tray_y = location.posy
            record.tray_matrix = {
                # x, y: position of the selected cell
                'selected': selected,
                # 0 is empty, 1 is not
                'cells': cells,
            }

    def _domain_move_lines_to_do(self):
        domain = [
            # TODO check state
            ('state', '=', 'assigned')
        ]
        domain_extensions = {
            'pick': [('location_id', 'child_of', self.location_id.id)],
            # TODO ensure that we cannot have the same ml in 2 shuttles (cannot
            # happen with 'pick' as they are in the shuttle's location)
            'put': [('location_dest_id', 'child_of', self.location_id.id)],
            # TODO
            'inventory': [('id', '=', 0)],
        }
        return domain + domain_extensions[self.mode]

    def _domain_move_lines_to_do_all(self):
        domain = [
            # TODO check state
            ('state', '=', 'assigned')
        ]
        # TODO search only in the view being a parent of shuttle's location
        shuttle_locations = self.env['stock.location'].search(
            [('vertical_lift_kind', '=', 'view')]
        )
        domain_extensions = {
            'pick': [('location_id', 'child_of', shuttle_locations.ids)],
            'put': [('location_dest_id', 'child_of', shuttle_locations.ids)],
            # TODO
            'inventory': [('id', '=', 0)],
        }
        return domain + domain_extensions[self.mode]

    def count_move_lines_to_do(self):
        self.ensure_one()
        return self.env['stock.move.line'].search_count(
            self._domain_move_lines_to_do()
        )

    def count_move_lines_to_do_all(self):
        self.ensure_one()
        return self.env['stock.move.line'].search_count(
            self._domain_move_lines_to_do_all()
        )

    def button_release(self):
        if self.current_move_line_id:
            self._hardware_switch_off_laser_pointer()
            self._hardware_close_tray()
        self.select_next_move_line()
        if not self.current_move_line_id:
            # sorry not sorry
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': _('Congrats, you cleared the queue!'),
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }

    def process_current_pick(self):
        # test code, TODO the smart one
        # (scan of barcode increments qty, save calls action_done?)
        line = self.current_move_line_id
        if line.state != 'done':
            line.qty_done = line.product_qty
            line.move_id._action_done()

    def process_current_put(self):
        raise exceptions.UserError(_('Put workflow not implemented'))

    def process_current_inventory(self):
        raise exceptions.UserError(_('Inventory workflow not implemented'))

    def button_save(self):
        if not (self and self.current_move_line_id):
            return
        self.ensure_one()
        method = 'process_current_{}'.format(self.mode)
        getattr(self, method)()
        self.operation_descr = _('Release')

    def select_next_move_line(self):
        self.ensure_one()
        next_move_line = self.env['stock.move.line'].search(
            self._domain_move_lines_to_do(), limit=1
        )
        self.current_move_line_id = next_move_line
        # TODO use a state machine to define next steps and
        # description?
        descr = (
            _('Scan New Destination Location')
            if next_move_line
            else _('No operations')
        )
        self.operation_descr = descr
        if next_move_line:
            self._hardware_switch_on_laser_pointer()
            self._hardware_open_tray()

    def action_open_screen(self):
        self.select_next_move_line()
        self.ensure_one()
        screen_xmlid = (
            'stock_vertical_lift.vertical_lift_shuttle_view_form_screen'
        )
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
        menu_xmlid = 'stock_vertical_lift.vertical_lift_shuttle_form_menu'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vertical.lift.shuttle',
            'views': [[self.env.ref(menu_xmlid).id, 'form']],
            'name': _('Menu'),
            'target': 'new',
            'res_id': self.id,
        }

    def action_manual_barcode(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vertical.lift.shuttle.manual.barcode',
            'view_mode': 'form',
            'name': _('Barcode'),
            'target': 'new',
        }

    # TODO: should the mode be changed on all the shuttles at the same time?
    def switch_pick(self):
        self.mode = 'pick'
        self.select_next_move_line()

    def switch_put(self):
        self.mode = 'put'
        self.select_next_move_line()

    def switch_inventory(self):
        self.mode = 'inventory'
        self.select_next_move_line()

    def _hardware_switch_on_laser_pointer(self):
        if self.hardware == 'simulation':
            self.env.user.notify_info(
                message=_('Laser pointer on x{} y{}').format(
                    self.tray_x, self.tray_y
                ),
                title=_('Lift Simulation'),
            )

    def _hardware_switch_off_laser_pointer(self):
        if self.hardware == 'simulation':
            self.env.user.notify_info(
                message=_('Switch off laser pointer'),
                title=_('Lift Simulation'),
            )

    def _hardware_open_tray(self):
        if self.hardware == 'simulation':
            self.env.user.notify_info(
                message=_('Opening tray {}').format(self.tray_name),
                title=_('Lift Simulation'),
            )

    def _hardware_close_tray(self):
        if self.hardware == 'simulation':
            self.env.user.notify_info(
                message=_('Closing tray {}').format(self.tray_name),
                title=_('Lift Simulation'),
            )


class VerticalLiftShuttleManualBarcode(models.TransientModel):
    _name = 'vertical.lift.shuttle.manual.barcode'
    _description = 'Action to input a barcode'

    barcode = fields.Char(string="Barcode")

    @api.multi
    def button_save(self):
        shuttle_id = self.env.context.get('active_id')
        shuttle = self.env['vertical.lift.shuttle'].browse(shuttle_id).exists()
        if not shuttle:
            return
        if self.barcode:
            shuttle.on_barcode_scanned(self.barcode)
