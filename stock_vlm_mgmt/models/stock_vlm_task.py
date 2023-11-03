# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from concurrent.futures import ThreadPoolExecutor, as_completed

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero


class VlmOperationTask(models.Model):
    _name = "stock.vlm.task"
    _inherit = ["vlm.tray.cell.position.mixin"]
    _description = "Vertical Lift Module task"

    display_name = fields.Char(compute="_compute_display_name")
    vlm_quant_id = fields.Many2one(comodel_name="stock.quant.vlm")
    quant_id = fields.Many2one(comodel_name="stock.quant")
    move_line_ids = fields.Many2many(comodel_name="stock.move.line")
    product_id = fields.Many2one(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")
    tray_id = fields.Many2one(comodel_name="stock.location.vlm.tray")
    tray_type_id = fields.Many2one(related="tray_id.tray_type_id")
    splitted_vlm_task_id = fields.Many2one(comodel_name="stock.vlm.task")
    quantity_pending = fields.Float(digits="Product Unit of Measure")
    quantity_done = fields.Float(digits="Product Unit of Measure")
    reference = fields.Char(default="")
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("waiting", "Waiting"),
            ("done", "Done"),
        ],
    )
    task_type = fields.Selection(
        selection=[
            ("put", "Put"),
            ("get", "Get"),
            ("count", "Count"),
        ],
    )
    skipped = fields.Boolean()

    @api.depends("task_type", "quantity_pending", "reference", "location_id", "tray_id")
    def _compute_display_name(self):
        """E.g.: WH/003: Put 80.0 Units of [RS200] Running socks in KARDEX ⇨ tray 31"""
        for task in self:
            qty = task.quantity_pending if task.state != "done" else task.quantity_done
            task.display_name = (
                f"{task.reference}: "
                f"{task.task_type.capitalize()} {qty} "
                f"{task.product_id.uom_id.name} of {task.product_id.display_name} "
                f"{'in' if task.task_type == 'put' else 'from'} "
                f"{task.location_id.name} ⇨ TRAY {task.tray_id.name}"
            )

    def action_command_task_threaded(self):
        # TODO: Not working, fails on environment or cursor things. Not usable
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            with ThreadPoolExecutor() as executor:
                futures = []
                for task in self:
                    futures.append(executor.submit(task.action_command_task))
                for future in as_completed(futures):
                    yield future.result()

    def action_command_task(self):
        """Send to the VLM then needed operations"""
        self.state = "waiting"
        pos_x, pos_y = self.tray_cell_center_position()
        response = self.location_id.send_vlm_request(
            self.location_id._prepare_vlm_request(
                task_type=self.task_type,
                carrier=self.tray_id.name,
                pos_x=pos_x,
                pos_y=pos_y,
                qty=self.quantity_pending,
                info1=self.reference,
                info2=self.product_id.display_name,
            )
        )
        # The only relevant thing we get in the response is the quantity
        return self._post_command(float(response.get("qty", "0")))

    def _post_command(self, quantity_done):
        """What to do depending on the VLM response"""
        quantity_compare = float_compare(
            quantity_done,
            self.quantity_pending,
            precision_rounding=self.product_id.uom_id.rounding,
        )
        # There could be several cases:
        # A) The done quantity is equal to the task quantity: task is done
        if quantity_compare == 0:
            self._set_done(quantity_done)
            # Set the pending quantity of the mls to 0
            self.move_line_ids.vlm_pending_quantity = 0
            self._update_quantities()
            return ("done", self)
        # B) The done quantity is lower than the task quantity:
        #   - Was the tray full?: propose another task
        #   - TODO: The quantity couldn't be fulfilled: the picking was wrong
        elif quantity_compare < 0:
            # Return it as it is
            if float_is_zero(quantity_done, self.product_id.uom_id.rounding):
                return ("zero_quantity", self)
            # Add an extra task for the remaining quantity and launch the wizard
            # so the user decides where to put them
            new_task = self._action_split(quantity_done)
            self._update_quantities()
            # Set the new task position and command it to the VLM
            return ("split", new_task)
        # C) Then done quantity is higher:
        #   - TODO: Was the picking was wrong?
        elif quantity_compare > 0:
            # Show the issue to the user
            if not self.env.context.get("skip_vlm_mismatch"):
                return (
                    "mismatch_greater",
                    self.with_context(vlm_task_action_warning="mismatch_greater"),
                )
            # TODO: Just confirm the qtys? Something else to do? It isnt't going
            # to match with the quant!
            self._set_done(quantity_done)
            self._update_quantities()

    def _set_done(self, quantity_done=None):
        quantity_done = quantity_done or self.quantity_pending
        self.quantity_pending = 0
        self.state = "done"
        self.quantity_done = quantity_done

    def _action_skip(self):
        """The task isn't done (it can be done later) or be finished manually"""
        self.skipped = True
        self.state = "done"

    def _action_split(self, quantity_done):
        """Divide a partially done task"""
        new_task = self.copy(
            {
                "quantity_pending": self.quantity_pending - quantity_done,
                "splitted_vlm_task_id": self.id,
                "state": "pending",
            }
        )
        self._set_done(quantity_done)
        return new_task

    def _update_quantities(self):
        if self.vlm_quant_id:
            if self.task_type == "put":
                self.vlm_quant_id.quantity += self.quantity_done
            elif self.task_type == "get":
                self.vlm_quant_id.quantity -= self.quantity_done
        elif self.task_type == "put":
            # For lots we should refine the search from the linked move lines
            quant = self.env["stock.quant"].search(
                [
                    ("location_id", "=", self.location_id.id),
                    ("product_id", "=", self.product_id.id),
                ],
                limit=1,
            )
            vlm_quant = self.env["stock.quant.vlm"].create(
                {
                    "quant_id": quant.id,
                    "product_id": self.product_id.id,
                    "location_id": self.location_id.id,
                    "tray_id": self.tray_id.id,
                    "pos_x": self.pos_x,
                    "pos_y": self.pos_y,
                    "quantity": self.quantity_done,
                }
            )
            self.quant_id = quant
            self.vlm_quant_id = vlm_quant

    def action_do_tasks(self):
        """Perform the tasks sequentially"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_vlm_mgmt.action_vlm_task_action"
        )
        tasks = self.filtered(lambda x: x.state != "done" or x.skipped)
        if not tasks:
            return
        action["name"] = f"VLM task {1} of {len(self.ids)}"
        action["context"] = dict(
            self.env.context,
            default_vlm_task_id=tasks.ids[0],
            default_vlm_task_ids=tasks.ids,
        )
        return action
