# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class VlmOperationTaskAction(models.TransientModel):
    _name = "stock.vlm.task.action"
    _inherit = ["vlm.tray.cell.position.mixin"]
    _description = "Actions to perform on vlm task exceptions"

    vlm_task_id = fields.Many2one(
        string="Selected task", comodel_name="stock.vlm.task", required=True
    )
    vlm_task_ids = fields.Many2many(comodel_name="stock.vlm.task")
    next_vlm_task_id = fields.Many2one(
        comodel_name="stock.vlm.task", compute="_compute_next_vlm_task_id"
    )
    previous_vlm_task_id = fields.Many2one(
        comodel_name="stock.vlm.task", compute="_compute_next_vlm_task_id"
    )
    splitted_vlm_task_id = fields.Many2one(
        comodel_name="stock.vlm.task", related="vlm_task_id.splitted_vlm_task_id"
    )
    image_512 = fields.Image(related="vlm_task_id.product_id.image_512")
    vlm_tasks_total = fields.Integer(compute="_compute_vlm_tasks_total")
    vlm_tasks_partial = fields.Integer(compute="_compute_vlm_tasks_total")
    vlm_tasks_progress = fields.Integer(compute="_compute_vlm_tasks_total")
    location_id = fields.Many2one(
        comodel_name="stock.location", related="vlm_task_id.location_id"
    )
    tray_id = fields.Many2one(comodel_name="stock.location.vlm.tray")
    quantity_pending = fields.Float(readonly=True)
    quantity_done = fields.Float()
    warning = fields.Char(readonly=True)
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("waiting", "Waiting"),
            ("done", "Done"),
            ("skipped", "Skipped"),
            ("edit", "Edit"),
        ],
        compute="_compute_state",
    )

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        task_id = self.env.context.get("default_vlm_task_id")
        task = self.env["stock.vlm.task"].browse(task_id)
        vals.update(
            {
                "pos_x": task.pos_x,
                "pos_y": task.pos_y,
                "quantity_done": task.quantity_done,
                "quantity_pending": task.quantity_pending,
                "tray_id": task.tray_id.id,
                "location_id": task.location_id.id,
                "tray_type_id": task.tray_id.tray_type_id.id,
            }
        )
        if not self.env.context.get("default_vlm_task_ids"):
            vals.update({"vlm_task_ids": [(6, 0, task.ids)]})
        warning = self.env.context.get("vlm_task_action_warning")
        if warning == "mismatch_greater":
            vals["warning"] = _(
                "Quantity mismatch! The quantity reported by the VLM is greater "
                "than original demand!. Please check it. If it's ok, you can fix "
                "it now and save the task manually."
            )
        return vals

    @api.depends("vlm_task_id", "vlm_task_ids")
    def _compute_next_vlm_task_id(self):
        self.next_vlm_task_id = False
        self.previous_vlm_task_id = False
        for wiz in self:
            # Value of vlm_tasks_partial is index + 1
            current_task_index = wiz.vlm_tasks_partial - 1
            if wiz.vlm_tasks_partial < wiz.vlm_tasks_total:
                wiz.next_vlm_task_id = wiz.vlm_task_ids[current_task_index + 1]
            # It isn't 0
            if current_task_index:
                wiz.previous_vlm_task_id = wiz.vlm_task_ids[current_task_index - 1]

    @api.depends("vlm_task_ids", "vlm_task_ids")
    def _compute_vlm_tasks_total(self):
        for wiz in self:
            wiz.vlm_tasks_total = len(wiz.vlm_task_ids)
            wiz.vlm_tasks_partial = wiz.vlm_task_ids.ids.index(wiz.vlm_task_id.id) + 1
            wiz.vlm_tasks_progress = (wiz.vlm_tasks_partial / wiz.vlm_tasks_total) * 100

    @api.depends("vlm_task_id.state", "vlm_task_id.skipped")
    def _compute_state(self):
        for wiz in self:
            if wiz.vlm_task_id.skipped:
                wiz.state = "skipped"
            elif self.env.context.get("vlm_wiz_edit_task"):
                wiz.state = "edit"
            else:
                wiz.state = wiz.vlm_task_id.state

    def action_command(self):
        """Set task values from the wizard"""
        self.vlm_task_id.pos_x = self.pos_x
        self.vlm_task_id.pos_y = self.pos_x
        self.vlm_task_id.tray_id = self.tray_id
        response, task = self.vlm_task_id.action_command_task()
        return self._check_post_command_task(response, task)

    def action_go_to_task(self, go_to="current"):
        """Go to the next task"""
        if go_to == "next":
            if not self.next_vlm_task_id:
                return {"type": "ir.actions.act_window_close"}
            idx = 1
            go_to_task = self.next_vlm_task_id
        elif go_to == "previous":
            if not self.previous_vlm_task_id:
                return {"type": "ir.actions.act_window_close"}
            idx = -1
            go_to_task = self.previous_vlm_task_id
        # Current task
        else:
            idx = 0
            go_to_task = self.vlm_task_id
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_vlm_mgmt.action_vlm_task_action"
        )
        action[
            "name"
        ] = f"VLM task {self.vlm_tasks_partial + idx} of {self.vlm_tasks_total}"
        action["context"] = dict(
            self.env.context,
            default_vlm_task_id=go_to_task.id,
            default_vlm_task_ids=self.vlm_task_ids.ids,
            default_warning=self.warning,
        )
        return action

    def action_next_task(self):
        return self.action_go_to_task(go_to="next")

    def action_previous_task(self):
        return self.action_go_to_task(go_to="previous")

    def action_skip_task(self):
        """Skip task and go to the next one"""
        self.vlm_task_id._action_skip()
        return self.action_next_task()

    def action_manual_set(self):
        """Save the info directly to the task as if it was validated by the VLM"""
        task = self.vlm_task_id
        if self.pos_x != task.pos_x or self.pos_y != task.pos_y:
            task.pos_x = self.pos_x
            task.pos_y = self.pos_y
        if self.tray_id != task.tray_id:
            task.tray_id = self.tray_id
        response, task = self.vlm_task_id._post_command(self.quantity_done)
        return self._check_post_command_task(response, task)

    def _set_warning_message(self, response):
        self.warning = False
        if response == "zero_quantity":
            self.warning = _(
                "No quantity was processed. Do you want to put the goods in another "
                "position? (you can also skip the task)"
            )
        elif response == "mismatch_greater":
            self.warning = _(
                "The quantity reported is greater than the one set in the task!"
            )

    def _check_post_command_task(self, response, task):
        """Either commanded or manual we want to perform the same tasks"""
        # Not all quantites were fulfilled. The task was splitted and we have to insert
        # it after our current task and then go to it to complete it.
        self._set_warning_message(response)
        if response == "split" and task.splitted_vlm_task_id == self.vlm_task_id:
            new_tasks_ids = self.vlm_task_ids.ids
            insert_index = new_tasks_ids.index(self.vlm_task_id.id) + 1
            new_tasks_ids[insert_index:insert_index] = [task.id]
            self.vlm_task_ids = self.vlm_task_ids.browse(new_tasks_ids)
            return self.action_next_task()
        return self.action_go_to_task(go_to="current")
