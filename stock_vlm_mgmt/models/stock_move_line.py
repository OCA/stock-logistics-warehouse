# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    has_vlm_operation = fields.Boolean(compute="_compute_has_vlm_operation")
    vlm_pending_quantity = fields.Float(
        help="Quantity pending on VLM Operations",
        default=0.0,
        digits="Product Unit of Measure",
        copy=False,
        store=True,
        readonly=False,
        compute="_compute_vlm_pending_quantity",
    )

    @api.depends("location_id", "location_dest_id")
    def _compute_has_vlm_operation(self):
        self.has_vlm_operation = False
        if self.env.context.get("skip_vlm_task"):
            return
        self.filtered(
            lambda x: x.location_id.is_vlm or x.location_dest_id.is_vlm
        ).has_vlm_operation = True

    @api.depends("qty_done")
    def _compute_vlm_pending_quantity(self):
        """Pair the reported quantities to the done ones"""
        # TODO: Maybe get rid of these and rely on operation task once they're created
        self.vlm_pending_quantity = 0
        for line in self.filtered("has_vlm_operation"):
            line.vlm_pending_quantity = line.qty_done

    def _prepare_vlm_put_task(self, key):
        """Over the recordset of detailed operations return a list of tasks to
        perform"""
        product, location = key
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", location.id),
            ]
        )
        # Get free spots
        # TODO: Sort them according to their strategy
        existing_quants = quants.vlm_quant_ids.filtered(lambda x: not x.tray_id.is_full)
        location_trays = location.vlm_tray_ids.filtered(lambda x: not x.is_full)
        # This is our demand for this product we'll try to fulfill it in one shot.
        # Anyway we could use other trays if one gets full
        quantity_fulfilled = sum(self.mapped("qty_done"))
        task_vlm_quant = fields.first(existing_quants)
        trays = location_trays - existing_quants.tray_id
        first_tray = task_vlm_quant.tray_id or fields.first(trays)
        if task_vlm_quant:
            pos_x = task_vlm_quant.pos_x
            pos_y = task_vlm_quant.pos_y
        else:
            pos_x, pos_y = first_tray.tray_matrix.get("first_empty_cell")
        return {
            "quantity_pending": quantity_fulfilled,
            "product_id": product.id,
            "state": "pending",
            "vlm_quant_id": task_vlm_quant.id,
            "location_id": first_tray.location_id.id,
            "reference": ",".join(self.mapped("reference")),
            "tray_id": first_tray.id,
            "pos_x": pos_x,
            "pos_y": pos_y,
            "move_line_ids": [(6, 0, self.ids)],
            "task_type": "put",
        }

    def _prepare_vlm_get_tasks(self, key):
        """Over the recordset of detailed operations return a list of tasks to
        perform"""
        product, location = key
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", location.id),
            ]
        )
        # TODO: Sort them according to their strategy
        # This is our demand for this product we'll try to fulfill it in one shot.
        # Anyway we could use other trays if one gets full
        pending_quantity = sum(self.mapped("qty_done"))
        tasks = []
        for vlm_quant in quants.vlm_quant_ids:
            qty = min(pending_quantity, vlm_quant.quantity)
            tasks.append(
                {
                    "quantity_pending": qty,
                    "product_id": product.id,
                    "state": "pending",
                    "vlm_quant_id": vlm_quant.id,
                    "tray_id": vlm_quant.tray_id.id,
                    "location_id": vlm_quant.location_id.id,
                    "quant_id": vlm_quant.quant_id.id,
                    "pos_x": vlm_quant.pos_x,
                    "pos_y": vlm_quant.pos_y,
                    "move_line_ids": [(6, 0, self.ids)],
                    "task_type": "get",
                    "reference": ",".join(self.mapped("reference")),
                }
            )
            pending_quantity -= qty
            if pending_quantity <= 0:
                break
        return tasks

    def _action_done(self):
        """Once we've completed our ml operations we need to complete them in the VLM.
        For that, we'll prepare the needed operations for each move line. Each move line
        could have several operations and one operation could correspond to several move
        lines. Some simple example:
        - A move line from vlm1 to vlm2 will split into two operations: one to get the
        products from vlm1 and another to put the products into vlm2.
        - If we've got several move lines for the same quant, we don't want to do an
        operation for each one. We'll try to merge them into a single operation so we
        minimize tray calls.
        """
        res = super()._action_done()
        if self.env.context.get("skip_vlm_task"):
            return res
        sml = self.exists()
        # 1. Prepare put operations
        put_in_vlm = sml.filtered(lambda x: x.qty_done and x.location_dest_id.is_vlm)
        # Let's group lines by common features. For this first design we don't care
        # about lot, owner, etc. Maybe in the feature this is relevant
        put_dict = defaultdict(self.browse)
        for line in put_in_vlm:
            put_dict[(line.product_id, line.location_dest_id)] += line
        put_task_values = []
        for key, lines in put_dict.items():
            put_task_values.append(lines._prepare_vlm_put_task(key))
        self.env["stock.vlm.task"].create(put_task_values)
        # 2. Prepare get operations
        get_from_vlm = sml.filtered(lambda x: x.qty_done and x.location_id.is_vlm)
        # TODO: Again we group lines by common features, merge into single method
        get_dict = defaultdict(self.browse)
        for line in get_from_vlm:
            get_dict[(line.product_id, line.location_id)] += line
        get_task_values = []
        for key, lines in get_dict.items():
            get_task_values += lines._prepare_vlm_get_tasks(key)
        self.env["stock.vlm.task"].create(get_task_values)
        return res
