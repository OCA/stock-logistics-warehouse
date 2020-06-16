# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    linked_reference = fields.Reference(
        selection=[("stock.picking", "stock.picking"), ("stock.move", "stock.move")],
        compute="_compute_linked_reference",
        readonly=True,
    )

    @api.depends("move_id.picking_id", "move_id")
    def _compute_linked_reference(self):
        for move_line in self:
            record = (
                move_line.move_id.picking_id
                if move_line.move_id.picking_id
                else move_line.move_id
            )
            if record:
                move_line.linked_reference = "{},{}".format(
                    record._name, record.id or 0
                )
            else:
                move_line.linked_reference = False
