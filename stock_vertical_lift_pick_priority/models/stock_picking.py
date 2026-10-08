# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def write(self, vals):
        if "priority" not in vals:
            return super().write(vals)
        priority_before = {picking: picking.priority for picking in self}
        res = super().write(vals)
        # A delivery that became more urgent must get its skipped lines back.
        # A lower priority changes nothing: stock_priority writes "0" on done
        # and cancelled transfers, that must not trigger a search.
        raised_priority = self.filtered(
            lambda picking: picking.picking_type_code == "outgoing"
            and int(picking.priority or "0") > int(priority_before[picking] or "0")
        )
        if raised_priority:
            # Bookkeeping of the shuttle: whoever raises the priority may not
            # have access to the vertical lift operations nor to the moves.
            operations = self.env["vertical.lift.operation.pick"].sudo().search([])
            for operation in operations:
                operation._unskip_lines_awaited_by(raised_priority.sudo())
        return res
