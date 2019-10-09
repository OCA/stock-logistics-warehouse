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


class VerticalLiftOperationTransfer(models.AbstractModel):
    """Base model for shuttle pick and put operations"""

    _name = "vertical.lift.operation.transfer"
    _inherit = "vertical.lift.operation.base"
    _description = "Vertical Lift Operation - Transfer"

    current_move_line_id = fields.Many2one(comodel_name="stock.move.line")

    number_of_ops = fields.Integer(
        compute="_compute_number_of_ops", string="Number of Operations"
    )
    number_of_ops_all = fields.Integer(
        compute="_compute_number_of_ops_all",
        string="Number of Operations in all shuttles",
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
                continue
            product = record.current_move_line_id.product_id
            values = {
                "packagings": [
                    {
                        "name": pkg.name,
                        "qty": pkg.qty,
                        "unit": product.uom_id.name,
                    }
                    for pkg in product.packaging_ids
                ]
            }
            content = self.env["ir.qweb"].render(
                "stock_vertical_lift.packagings", values
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

    @api.depends("tray_location_id", "current_move_line_id.product_id")
    def _compute_tray_qty(self):
        for record in self:
            if not (record.tray_location_id and record.current_move_line_id):
                continue
            product = record.current_move_line_id.product_id
            quants = self.env["stock.quant"].search(
                [
                    ("location_id", "=", record.tray_location_id.id),
                    ("product_id", "=", product.id),
                ]
            )
            record.tray_qty = sum(quants.mapped("quantity"))

    # depends of the quantity so we can't have all triggers
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
        self.select_next_move_line()

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
        return

    def select_next_move_line(self):
        self.ensure_one()
        next_move_line = self.env["stock.move.line"].search(
            self._domain_move_lines_to_do(), limit=1
        )
        self.current_move_line_id = next_move_line
        # TODO use a state machine to define next steps and
        # description?
        descr = (
            _("Scan New Destination Location")
            if next_move_line
            else _("No operations")
        )
        self.operation_descr = descr
        if next_move_line:
            self.fetch_tray()
