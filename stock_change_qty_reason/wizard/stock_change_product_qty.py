# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockChangeProductQty(models.TransientModel):
    """Class to inherit model stock.change.product.qty"""

    _inherit = "stock.change.product.qty"

    reason = fields.Char(help="Type in a reason for the " "product quantity change")
    preset_reason_id = fields.Many2one("stock.inventory.line.reason")

    @api.multi
    def change_product_qty(self):
        """Function to super change_product_qty"""
        if self.reason:
            this = self.with_context(change_quantity_reason=self.reason)
            return super(StockChangeProductQty, this).change_product_qty()
        return super(StockChangeProductQty, self).change_product_qty()

    def _action_start_line(self):
        res = super(StockChangeProductQty, self)._action_start_line()
        if self.preset_reason_id:
            res.update(
                {
                    "preset_reason_id": self.preset_reason_id.id,
                    "reason": self.preset_reason_id.name,
                }
            )
        elif self.reason:
            res.update({"reason": self.reason})
        return res

    @api.onchange("preset_reason_id")
    def onchange_preset_reason_id(self):
        if self.preset_reason_id:
            self.reason = self.preset_reason_id.name
