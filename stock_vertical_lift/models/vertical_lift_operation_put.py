# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.osv import expression


class VerticalLiftOperationPut(models.Model):
    _name = "vertical.lift.operation.put"
    _inherit = "vertical.lift.operation.transfer"
    _description = "Vertical Lift Operation Put"

    operation_line_ids = fields.One2many(
        comodel_name="vertical.lift.operation.put.line",
        inverse_name="operation_id",
        readonly=True,
    )
    current_operation_line_id = fields.Many2one(
        comodel_name="vertical.lift.operation.put.line", readonly=True
    )
    current_move_line_id = fields.Many2one(
        related="current_operation_line_id.move_line_id", readonly=True
    )
    # TODO think about moving the "steps" to the base model,
    # integrate 'save' and 'release' in 'next_step()', use states
    # in 'pick' as well
    state = fields.Selection(
        selection=[
            ("scan_product", "Scan Product"),
            ("scan_tray_type", "Scan Tray Type"),
            ("save", "Save"),
            ("release", "Release"),
        ],
        default="scan_product",
    )

    next_operation = object()

    def _transitions(self):
        return {
            "scan_product": "scan_tray_type",
            "scan_tray_type": "save",
            "save": "release",
            "release": self.next_operation,
        }

    # The steps cannot be in 'vertical.lift.operation.put.line' because the
    # state has to be modified by on_barcode_scanned. As this method is an
    # onchange underneath, it has to be on the same model.
    def step(self):
        return self.state

    def next_step(self):
        next_state = self._transitions().get(self.state)
        if next_state is not self.next_operation:
            self.state = next_state
        self.update_step_description()

    def step_description(self):
        state_field = self._fields["state"]
        return state_field.convert_to_export(self.state, self)

    def reset_steps(self):
        self.state = "scan_product"
        self.update_step_description()

    def count_move_lines_to_do(self):
        """Count move lines to process in current shuttle"""
        self.ensure_one()
        return self.env["vertical.lift.operation.put.line"].search_count(
            [("operation_id", "=", self.id)]
        )

    def count_move_lines_to_do_all(self):
        """Count move lines to process in all shuttles"""
        self.ensure_one()
        return self.env["vertical.lift.operation.put.line"].search_count([])

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        operation_line = self.current_operation_line_id
        if operation_line:
            if self.step() == "scan_product":
                if self._check_product(barcode):
                    self.next_step()
            if self.step() == "scan_tray_type":
                if self._check_tray_type(barcode):
                    self.next_step()

    def _check_product(self, barcode):
        return barcode == self.current_move_line_id.product_id.barcode

    def _check_tray_type(self, barcode):
        location = self.current_move_line_id.location_dest_id
        tray_type = location.cell_in_tray_type_id
        return barcode == tray_type.code

    def update_step_description(self):
        if self.current_operation_line_id:
            descr = self.step_description()
        else:
            descr = _("No operations")
        self.operation_descr = descr

    def fetch_tray(self):
        self.current_move_line_id.fetch_vertical_lift_tray_dest()

    def process_current(self):
        self.current_operation_line_id.process()

    def button_release(self):
        self.write({"operation_line_ids": [(2, self.current_operation_line_id.id)]})
        return super().button_release()

    def button_save(self):
        if not (self and self.current_operation_line_id):
            return
        self.ensure_one()
        self.process_current()
        self.next_step()

    def on_screen_open(self):
        """Called when the screen is open"""
        if self.operation_line_ids:
            self.select_next_move_line()
        else:
            return self.action_select_operations()

    def select_next_move_line(self):
        self.ensure_one()
        next_operation = fields.first(self.operation_line_ids)
        self.current_operation_line_id = next_operation
        self.reset_steps()
        if next_operation:
            self.fetch_tray()

    def action_select_operations(self):
        self.ensure_one()
        menu_xmlid = "stock_vertical_lift." "vertical_lift_operation_put_select_view"
        select_model = self.env["vertical.lift.operation.put.select"]
        select = select_model.create(
            {
                "operation_id": self.id,
                "move_line_ids": [
                    (6, 0, self.mapped("operation_line_ids.move_line_id.id"))
                ],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "vertical.lift.operation.put.select",
            "views": [[self.env.ref(menu_xmlid).id, "form"]],
            "name": _("Scan Operations"),
            "target": "new",
            "res_id": select.id,
        }


class VerticalLiftOperationPutLine(models.Model):
    _name = "vertical.lift.operation.put.line"
    _description = "Vertical Lift Operation Put Line"

    operation_id = fields.Many2one(
        comodel_name="vertical.lift.operation.put", required=True, readonly=True
    )
    move_line_id = fields.Many2one(comodel_name="stock.move.line", readonly=True)

    def process(self):
        line = self.move_line_id
        if line.state != "done":
            line.qty_done = line.product_qty
            line.move_id._action_done()


class VerticalLiftOperationPutSelect(models.TransientModel):
    _name = "vertical.lift.operation.put.select"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Vertical Lift Operation Put Select"

    operation_id = fields.Many2one(
        comodel_name="vertical.lift.operation.put", required=True, readonly=True
    )
    move_line_ids = fields.Many2many(comodel_name="stock.move.line")

    def _sync_lines(self):
        self.operation_id.operation_line_ids.unlink()
        operation_line_model = self.env["vertical.lift.operation.put.line"]
        operation_line_model.create(
            [
                {"operation_id": self.operation_id.id, "move_line_id": move_line.id}
                for move_line in self.move_line_ids
            ]
        )
        self.operation_id.select_next_move_line()

    def action_validate(self):
        self._sync_lines()
        return {"type": "ir.actions.act_window_close"}

    def _move_line_domain(self):
        return [
            ("state", "=", "assigned"),
            ("location_dest_id", "child_of", self.operation_id.location_id.id),
        ]

    def action_add_all(self):
        move_lines = self.env["stock.move.line"].search(self._move_line_domain())
        self.move_line_ids = move_lines
        self._sync_lines()
        return {"type": "ir.actions.act_window_close"}

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        domain = self._move_line_domain()
        domain = expression.AND([domain, [("product_id.barcode", "=", barcode)]])
        move_lines = self.env["stock.move.line"].search(domain)
        # note: on_barcode_scanned is called in an onchange, so 'self'
        # is a NewID, we can't use 'write()' on it.
        self.move_line_ids |= move_lines
