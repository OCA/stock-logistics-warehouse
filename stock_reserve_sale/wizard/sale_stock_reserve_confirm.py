from odoo import fields, models
from odoo.tools import float_compare


class SaleStockReserveConfirm(models.TransientModel):
    _name = "sale.stock.reserve.confirm"
    _description = "Confirm Stock Reservation"

    reserve_id = fields.Many2one("sale.stock.reserve", required=True)

    def action_confirm(self):
        self.ensure_one()
        lines = self.reserve_id.line_ids.filtered(
            lambda line: float_compare(
                line.quantity,
                line.product_uom_qty,
                precision_rounding=line.product_uom.rounding,
            )
            > 0
        )
        for line in lines:
            line.sale_line_id.write({"product_uom_qty": line.quantity})
        # The related ordered quantity of the wizard lines is not refreshed
        # automatically after writing on the sale lines.
        self.reserve_id.line_ids.invalidate_recordset(["product_uom_qty"])
        return self.reserve_id.button_reserve()
