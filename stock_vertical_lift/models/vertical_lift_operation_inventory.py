# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare

from odoo.addons.base_sparse_field.models.fields import Serialized

# TODO handle autofocus + easy way to validate for the input field


class VerticalLiftOperationInventory(models.Model):
    _name = "vertical.lift.operation.inventory"
    _inherit = "vertical.lift.operation.base"
    _description = "Vertical Lift Operation Inventory"

    _initial_state = "noop"

    def _selection_states(self):
        return [
            ("noop", "No inventory in progress"),
            ("quantity", "Inventory, please enter the amount"),
            ("confirm_wrong_quantity", "The quantity does not match, are you sure?"),
            # save is never visible, but save and go to the next or noop directly
            ("save", "Save"),
            # no need for release and save button here?
            # ("release", "Release"),
        ]

    def _transitions(self):
        return (
            self.Transition(
                "noop",
                "quantity",
                # transition only if inventory lines are found
                lambda self: self.select_next_inventory_line(),
            ),
            self.Transition(
                "quantity",
                "save",
                lambda self: self._has_identical_quantity(),
            ),
            self.Transition(
                "quantity",
                "confirm_wrong_quantity",
                lambda self: self._start_confirm_wrong_quantity(),
            ),
            self.Transition(
                "confirm_wrong_quantity",
                "save",
                lambda self: self.quantity_input == self.last_quantity_input,
            ),
            # if the confirmation of the quantity is different, cycle back to
            # the 'quantity' step
            self.Transition(
                "confirm_wrong_quantity",
                "quantity",
                lambda self: self._go_back_to_quantity_input(),
            ),
            # go to quantity if we have lines in queue, otherwise, go to noop
            self.Transition(
                "save",
                "quantity",
                lambda self: self.process_current()
                and self.select_next_inventory_line(),
                # when we reach 'save', this transition is directly
                # evaluated
                direct_eval=True,
            ),
            self.Transition(
                "save",
                "noop",
                lambda self: self.process_current()
                and self.clear_current_inventory_line(),
                # when we reach 'save', this transition is directly
                # evaluated
                direct_eval=True,
            ),
        )

    current_inventory_line_id = fields.Many2one(
        comodel_name="stock.inventory.line", readonly=True
    )

    quantity_input = fields.Float()
    # if the quantity is wrong, user has to write 2 times
    # the same quantity to really confirm it's correct
    last_quantity_input = fields.Float()

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
    tray_type_code = fields.Char(compute="_compute_tray_data", string="Tray Code")
    tray_x = fields.Integer(string="X", compute="_compute_tray_data")
    tray_y = fields.Integer(string="Y", compute="_compute_tray_data")
    tray_matrix = Serialized(string="Cells", compute="_compute_tray_data")
    tray_qty = fields.Float(string="Stock Quantity", compute="_compute_tray_qty")

    # current operation information
    inventory_id = fields.Many2one(
        related="current_inventory_line_id.inventory_id", readonly=True
    )
    product_id = fields.Many2one(
        related="current_inventory_line_id.product_id", readonly=True
    )
    product_uom_id = fields.Many2one(
        related="current_inventory_line_id.product_uom_id", readonly=True
    )
    product_qty = fields.Float(
        related="current_inventory_line_id.product_qty", readonly=True
    )
    product_packagings = fields.Html(
        string="Packaging", compute="_compute_product_packagings"
    )
    package_id = fields.Many2one(
        related="current_inventory_line_id.package_id", readonly=True
    )
    lot_id = fields.Many2one(
        related="current_inventory_line_id.prod_lot_id", readonly=True
    )

    @api.depends("current_inventory_line_id")
    def _compute_tray_data(self):
        for record in self:
            location = record.current_inventory_line_id.location_id
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

    @api.depends("current_inventory_line_id.product_id.packaging_ids")
    def _compute_product_packagings(self):
        for record in self:
            product = record.current_inventory_line_id.product_id
            if not product:
                record.product_packagings = ""
                continue
            content = self._render_product_packagings(product)
            record.product_packagings = content

    @api.depends("tray_location_id", "current_inventory_line_id.product_id")
    def _compute_tray_qty(self):
        for record in self:
            if not (record.tray_location_id and record.current_inventory_line_id):
                record.tray_qty = 0.0
                continue
            product = record.current_inventory_line_id.product_id
            location = record.tray_location_id
            record.tray_qty = self._get_tray_qty(product, location)

    def _compute_number_of_ops(self):
        for record in self:
            line_model = self.env["stock.inventory.line"]
            record.number_of_ops = line_model.search_count(
                self._domain_inventory_lines_to_do()
            )

    def _compute_number_of_ops_all(self):
        for record in self:
            line_model = self.env["stock.inventory.line"]
            record.number_of_ops_all = line_model.search_count(
                self._domain_inventory_lines_to_do_all()
            )

    def _domain_inventory_lines_to_do(self):
        return [
            ("location_id", "child_of", self.location_id.id),
            ("state", "=", "confirm"),
            ("vertical_lift_done", "=", False),
        ]

    def _domain_inventory_lines_to_do_all(self):
        shuttle_locations = self.env["stock.location"].search(
            [("vertical_lift_kind", "=", "view")]
        )
        return [
            ("location_id", "child_of", shuttle_locations.ids),
            ("state", "=", "confirm"),
            ("vertical_lift_done", "=", False),
        ]

    def reset_steps(self):
        self.clear_current_inventory_line()
        super().reset_steps()

    def _has_identical_quantity(self):
        line = self.current_inventory_line_id
        return (
            float_compare(
                line.theoretical_qty,
                self.quantity_input,
                precision_rounding=line.product_uom_id.rounding,
            )
            == 0
        )

    def _start_confirm_wrong_quantity(self):
        self.last_quantity_input = self.quantity_input
        self.quantity_input = 0.0
        return True

    def _go_back_to_quantity_input(self):
        self.last_quantity_input = self.quantity_input
        self.quantity_input = 0.0
        return True

    def clear_current_inventory_line(self):
        self.write(
            {
                "quantity_input": 0.0,
                "last_quantity_input": 0.0,
                "current_inventory_line_id": False,
            }
        )
        return True

    def fetch_tray(self):
        location = self.current_inventory_line_id.location_id
        location.fetch_vertical_lift_tray()

    def select_next_inventory_line(self):
        self.ensure_one()
        next_line = self.env["stock.inventory.line"].search(
            self._domain_inventory_lines_to_do(),
            limit=1,
            order="vertical_lift_tray_id, location_id, id",
        )
        self.current_inventory_line_id = next_line
        if next_line:
            self.fetch_tray()
        return bool(next_line)

    def process_current(self):
        line = self.current_inventory_line_id
        if not line.vertical_lift_done:
            line.vertical_lift_done = True
            if self.quantity_input != line.product_qty:
                line.product_qty = self.quantity_input
            inventory = line.inventory_id
            if all(line.vertical_lift_done for line in inventory.line_ids):
                inventory.action_validate()
            self.quantity_input = self.last_quantity_input = 0.0
        return True

    def button_save(self):
        self.ensure_one()
        if not self.step() in ("quantity", "confirm_wrong_quantity"):
            return
        self.next_step()
        if self.step() == "noop":
            # close the tray once everything is inventoried
            self.shuttle_id.release_vertical_lift_tray()
            # sorry not sorry
            return self._rainbow_man()
