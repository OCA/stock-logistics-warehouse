# Copyright 2019 Camptocamp SA
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero

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

    quant_id = fields.Many2one("stock.quant", string="Current Quant")

    quantity_input = fields.Float()
    # if the quantity is wrong, user has to write 2 times
    # the same quantity to really confirm it's correct
    last_quantity_input = fields.Float()

    tray_location_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_tray_data",
        string="Tray Location",
    )
    tray_name = fields.Char(compute="_compute_tray_data")
    tray_type_id = fields.Many2one(
        comodel_name="stock.location.tray.type",
        compute="_compute_tray_data",
        string="Tray Type",
    )
    tray_type_code = fields.Char(compute="_compute_tray_data", string="Tray Code")
    tray_x = fields.Integer(string="X", compute="_compute_tray_data")
    tray_y = fields.Integer(string="Y", compute="_compute_tray_data")
    tray_matrix = fields.Json(string="Cells", compute="_compute_tray_data")
    tray_qty = fields.Float(string="Stock Quantity", compute="_compute_tray_qty")

    product_id = fields.Many2one(related="quant_id.product_id")
    product_uom_id = fields.Many2one(related="quant_id.product_uom_id")
    product_qty = fields.Float(related="quant_id.inventory_quantity")
    product_packagings = fields.Html(
        string="Packaging", compute="_compute_product_packagings"
    )
    package_id = fields.Many2one(related="quant_id.package_id")
    lot_id = fields.Many2one(related="quant_id.lot_id")

    @api.depends("quant_id")
    def _compute_tray_data(self):
        for record in self:
            location = record.quant_id.location_id
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

    @api.depends("quant_id.product_id.packaging_ids")
    def _compute_product_packagings(self):
        for record in self:
            product = record.quant_id.product_id
            if not product:
                record.product_packagings = ""
                continue
            content = self._render_product_packagings(product)
            record.product_packagings = content

    @api.depends("tray_location_id", "quant_id.product_id")
    def _compute_tray_qty(self):
        for record in self:
            if not (record.tray_location_id and record.quant_id):
                record.tray_qty = 0.0
                continue
            product = record.quant_id.product_id
            location = record.tray_location_id
            record.tray_qty = self._get_tray_qty(product, location)

    def _compute_number_of_ops(self):
        for record in self:
            quant_model = self.env["stock.quant"]
            record.number_of_ops = quant_model.search_count(
                self._domain_stock_quant_to_do()
            )

    def _compute_number_of_ops_all(self):
        for record in self:
            quant_model = self.env["stock.quant"]
            record.number_of_ops_all = quant_model.search_count(
                self._domain_inventory_lines_to_do_all()
            )

    def _domain_stock_quant_to_do(self):
        return [
            ("location_id", "child_of", self.location_id.id),
            ("inventory_quantity_set", "=", True),
            ("vertical_lift_done", "=", False),
        ]

    def _domain_inventory_lines_to_do_all(self):
        shuttle_locations = self.env["stock.location"].search(
            [("vertical_lift_kind", "=", "view")]
        )
        return [
            ("location_id", "child_of", shuttle_locations.ids),
            ("inventory_quantity_set", "=", True),
            ("vertical_lift_done", "=", False),
        ]

    def reset_steps(self):
        self.clear_current_inventory_line()
        return super().reset_steps()

    def _has_identical_quantity(self):
        stock_quant = self.quant_id
        rounding = stock_quant.quantity - self.quantity_input
        return float_is_zero(
            rounding,
            precision_rounding=stock_quant.product_uom_id.rounding,
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
                "quant_id": False,
            }
        )
        return True

    def fetch_tray(self):
        location = self.quant_id.location_id
        location.fetch_vertical_lift_tray()

    def select_next_inventory_line(self):
        self.ensure_one()
        next_quant_id = self.env["stock.quant"].search(
            self._domain_stock_quant_to_do(),
            limit=1,
            order="vertical_lift_tray_id, location_id, id",
        )
        self.quant_id = next_quant_id
        if next_quant_id:
            self.fetch_tray()
        return bool(next_quant_id)

    def process_current(self):
        quant = self.quant_id
        if quant and not quant.vertical_lift_done:
            quant.vertical_lift_done = True
            if (
                float_compare(
                    self.quantity_input,
                    quant.quantity,
                    precision_rounding=quant.product_uom_id.rounding,
                )
                != 0
            ):
                quant.inventory_quantity = self.quantity_input
                quant._apply_inventory()
            self.quantity_input = self.last_quantity_input = 0.0
        return True

    def button_save(self):
        self.ensure_one()
        if self.step() not in ("quantity", "confirm_wrong_quantity"):
            return
        self.next_step()
        if self.step() == "noop":
            # close the tray once everything is inventoried
            self.shuttle_id.release_vertical_lift_tray()
            # sorry not sorry
            return self._rainbow_man()
