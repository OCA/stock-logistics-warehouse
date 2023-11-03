# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    vlm_move_line_ids = fields.Many2many(
        comodel_name="stock.move.line", compute="_compute_vlm_move_line_ids"
    )
    vlm_pending_move_line_ids = fields.Many2many(
        comodel_name="stock.move.line", compute="_compute_vlm_move_line_ids"
    )
    has_vlm_operations = fields.Boolean(compute="_compute_has_vlm_operations")
    has_vlm_pending_operations = fields.Boolean(
        compute="_compute_has_vlm_pending_operations"
    )
    vlm_task_ids = fields.Many2many(
        comodel_name="stock.vlm.task",
        compute="_compute_vlm_task_ids",
    )
    has_pending_vlm_tasks = fields.Boolean(compute="_compute_has_pending_vlm_tasks")

    @api.depends("location_id", "location_dest_id")
    def _compute_vlm_move_line_ids(self):
        for pick in self:
            pick.vlm_move_line_ids = pick.move_line_ids.filtered(
                lambda x: x.location_id.is_vlm or x.location_dest_id.is_vlm
            )
            pick.vlm_pending_move_line_ids = pick.vlm_move_line_ids.filtered(
                "vlm_pending_quantity"
            )

    @api.depends("vlm_move_line_ids")
    def _compute_has_vlm_operations(self):
        for pick in self:
            pick.has_vlm_operations = bool(pick.vlm_move_line_ids)

    @api.depends("vlm_pending_move_line_ids")
    def _compute_has_vlm_pending_operations(self):
        """We need to complete the quantities in the VLM"""
        self.has_vlm_pending_operations = False
        for pick in self.filtered(lambda x: x.state == "done"):
            pick.has_vlm_pending_operations = bool(pick.vlm_pending_move_line_ids)

    @api.depends("state")
    def _compute_vlm_task_ids(self):
        self.vlm_task_ids = False
        for pick in self.filtered(lambda x: x.state == "done"):
            pick.vlm_task_ids = self.env["stock.vlm.task"].search(
                [
                    ("move_line_ids", "in", pick.move_line_ids.ids),
                ]
            )

    def _compute_has_pending_vlm_tasks(self):
        """Helper to show the task action button"""
        self.has_pending_vlm_tasks = False
        for pick in self:
            pick.has_pending_vlm_tasks = bool(
                pick.vlm_task_ids.filtered(lambda x: x.state != "done")
            )

    def action_do_vlm_tasks(self):
        """Perform the VLM pending tasks"""
        return self.vlm_task_ids.filtered(lambda x: x.state != "done").action_do_tasks()

    def action_open_vlm_task(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_vlm_mgmt.vlm_task_action"
        )
        # Let's pre-sort the task so we always first get and then put. i.e.: when we're
        # moving goods from one VLM to another
        get_tasks = self.vlm_task_ids.filtered(lambda x: x.task_type == "get").sorted(
            lambda x: (x.location_id, x.tray_id, x.product_id)
        )
        put_tasks = self.vlm_task_ids.filtered(lambda x: x.task_type == "put").sorted(
            lambda x: (x.location_id, x.tray_id, x.product_id)
        )
        vlm_tasks = get_tasks + put_tasks
        action["name"] = f"SVM tasks for {self.name}"
        action["domain"] = [("id", "in", vlm_tasks.ids)]
        action["context"] = dict(self.env.context, search_default_pending=1)
        return action
