# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class VerticalLiftOperationBase(models.AbstractModel):
    """Base model for shuttle operations (pick, put, inventory)"""

    _name = "vertical.lift.operation.base"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Vertical Lift Operation - Base"

    name = fields.Char(related="shuttle_id.name", readonly=True)
    shuttle_id = fields.Many2one(
        comodel_name="vertical.lift.shuttle", required=True, readonly=True
    )
    location_id = fields.Many2one(
        related="shuttle_id.location_id", readonly=True
    )
    number_of_ops = fields.Integer(
        compute="_compute_number_of_ops", string="Number of Operations"
    )
    number_of_ops_all = fields.Integer(
        compute="_compute_number_of_ops_all",
        string="Number of Operations in all shuttles",
    )
    mode = fields.Selection(related="shuttle_id.mode", readonly=True)
    operation_descr = fields.Char(
        string="Operation", default="...", readonly=True
    )

    _sql_constraints = [
        (
            "shuttle_id_unique",
            "UNIQUE(shuttle_id)",
            "One pick can be run at a time for a shuttle.",
        )
    ]

    @api.depends()
    def _compute_number_of_ops(self):
        for record in self:
            record.number_of_ops = 0

    @api.depends()
    def _compute_number_of_ops_all(self):
        for record in self:
            record.number_of_ops_all = 0

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        # to implement in sub-classes

    def on_screen_open(self):
        """Called when the screen is open

        To implement in sub-classes.
        """

    def action_open_screen(self):
        return self.shuttle_id.action_open_screen()

    def action_menu(self):
        return self.shuttle_id.action_menu()

    def action_manual_barcode(self):
        return self.shuttle_id.action_manual_barcode()

    def button_save(self):
        """Process the action (pick, put, ...)"""
        raise NotImplementedError

    def button_release(self):
        """Release the operation, go to the next"""
        raise NotImplementedError

    def _render_product_packagings(self, product):
        values = {
            "packagings": [
                {"name": pkg.name, "qty": pkg.qty, "unit": product.uom_id.name}
                for pkg in product.packaging_ids
            ]
        }
        content = self.env["ir.qweb"].render(
            "stock_vertical_lift.packagings", values
        )
        return content

    def _get_tray_qty(self, product, location):
        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", location.id),
                ("product_id", "=", product.id),
            ]
        )
        return sum(quants.mapped("quantity"))

    def _send_notification_refresh(self):
        """Send a refresh notification

        Generally, you want to call the method
        _send_notification_refresh() on VerticalLiftShuttle so you
        don't need to know the id of the current operation.

        Other notifications can be implemented, they have to be
        added in static/src/js/vertical_lift.js and the message
        must contain an "action" and "params".
        """
        self.ensure_one()
        channel = "notify_vertical_lift_screen"
        bus_message = {
            "action": "refresh",
            "params": {
                "model": self._name,
                "id": self.id,
            }
        }
        self.env["bus.bus"].sendone(channel, bus_message)


class VerticalLiftOperationTransfer(models.AbstractModel):
    """Base model for shuttle pick and put operations"""

    _name = "vertical.lift.operation.transfer"
    _inherit = "vertical.lift.operation.base"
    _description = "Vertical Lift Operation - Transfer"

    current_move_line_id = fields.Many2one(
        comodel_name="stock.move.line", readonly=True
    )

    tray_location_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_tray_data",
        string="Tray Location",
    )
    tray_name = fields.Char(compute="_compute_tray_data", string="Tray Name")
    tray_type_id = fields.Many2one(
        comodel_name="stock.location.tray.type",
        compute="_compute_tray_data",
        string="Tray Type",
    )
    tray_type_code = fields.Char(
        compute="_compute_tray_data", string="Tray Code"
    )
    tray_x = fields.Integer(string="X", compute="_compute_tray_data")
    tray_y = fields.Integer(string="Y", compute="_compute_tray_data")
    tray_matrix = Serialized(string="Cells", compute="_compute_tray_data")
    tray_qty = fields.Float(
        string="Stock Quantity", compute="_compute_tray_qty"
    )

    # current operation information
    picking_id = fields.Many2one(
        related="current_move_line_id.picking_id", readonly=True
    )
    picking_origin = fields.Char(
        related="current_move_line_id.picking_id.origin", readonly=True
    )
    picking_partner_id = fields.Many2one(
        related="current_move_line_id.picking_id.partner_id", readonly=True
    )
    product_id = fields.Many2one(
        related="current_move_line_id.product_id", readonly=True
    )
    product_uom_id = fields.Many2one(
        related="current_move_line_id.product_uom_id", readonly=True
    )
    product_uom_qty = fields.Float(
        related="current_move_line_id.product_uom_qty", readonly=True
    )
    product_packagings = fields.Html(
        string="Packaging", compute="_compute_product_packagings"
    )
    qty_done = fields.Float(
        related="current_move_line_id.qty_done", readonly=True
    )
    lot_id = fields.Many2one(
        related="current_move_line_id.lot_id", readonly=True
    )
    location_dest_id = fields.Many2one(
        string="Destination",
        related="current_move_line_id.location_dest_id",
        readonly=True,
    )
    # TODO add a glue addon with product_expiry to add the field

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        self.env.user.notify_info(
            "Scanned barcode: {}. Not implemented.".format(barcode)
        )

    @api.depends("current_move_line_id.product_id.packaging_ids")
    def _compute_product_packagings(self):
        for record in self:
            if not record.current_move_line_id:
                record.product_packagings = ""
                continue
            product = record.current_move_line_id.product_id
            content = self._render_product_packagings(product)
            record.product_packagings = content

    @api.depends()
    def _compute_number_of_ops(self):
        for record in self:
            record.number_of_ops = record.count_move_lines_to_do()

    @api.depends()
    def _compute_number_of_ops_all(self):
        for record in self:
            record.number_of_ops_all = record.count_move_lines_to_do_all()

    @api.depends("tray_location_id", "current_move_line_id.product_id")
    def _compute_tray_qty(self):
        for record in self:
            if not (record.tray_location_id and record.current_move_line_id):
                record.tray_qty = 0.
                continue
            product = record.current_move_line_id.product_id
            location = record.tray_location_id
            record.tray_qty = self._get_tray_qty(product, location)

    @api.depends("current_move_line_id")
    def _compute_tray_data(self):
        for record in self:
            modes = {"pick": "location_id", "put": "location_dest_id"}
            location = record.current_move_line_id[modes[record.mode]]
            tray_type = location.location_id.tray_type_id
            # this is the current cell
            record.tray_location_id = location.id
            # name of the tray where the cell is
            record.tray_name = location.location_id.name
            record.tray_type_id = tray_type.id
            record.tray_type_code = tray_type.code
            record.tray_x = location.posx
            record.tray_y = location.posy
            record.tray_matrix = location.tray_matrix

    def _domain_move_lines_to_do(self):
        # to implement in sub-classes
        return [("id", "=", 0)]

    def _domain_move_lines_to_do_all(self):
        # to implement in sub-classes
        return [("id", "=", 0)]

    def count_move_lines_to_do(self):
        """Count move lines to process in current shuttles"""
        self.ensure_one()
        return self.env["stock.move.line"].search_count(
            self._domain_move_lines_to_do()
        )

    def count_move_lines_to_do_all(self):
        """Count move lines to process in all shuttles"""
        self.ensure_one()
        return self.env["stock.move.line"].search_count(
            self._domain_move_lines_to_do_all()
        )

    def on_screen_open(self):
        """Called when the screen is open"""

    def button_release(self):
        """Release the operation, go to the next"""
        self.select_next_move_line()
        if not self.current_move_line_id:
            # sorry not sorry
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": _("Congrats, you cleared the queue!"),
                    "img_url": "/web/static/src/img/smile.svg",
                    "type": "rainbow_man",
                }
            }

    def process_current(self):
        raise NotImplementedError

    def button_save(self):
        if not (self and self.current_move_line_id):
            return
        self.ensure_one()
        self.process_current()
        self.operation_descr = _("Release")

    def fetch_tray(self):
        raise NotImplementedError
