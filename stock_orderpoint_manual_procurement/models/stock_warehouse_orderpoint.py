# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.tools import float_compare, float_round


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    procure_recommended_qty = fields.Float(
        string="Procure Recommendation",
        compute="_compute_procure_recommended",
        digits="Product Unit of Measure",
    )
    procure_recommended_date = fields.Date(
        string="Recommended Request Date", compute="_compute_procure_recommended"
    )

    def _get_procure_recommended_qty(self, virtual_qty, op_qtys):
        self.ensure_one()
        procure_recommended_qty = 0.0
        qty = max(self.product_min_qty, self.product_max_qty) - virtual_qty
        remainder = self.qty_multiple > 0 and qty % self.qty_multiple or 0.0
        if (
            float_compare(remainder, 0.0, precision_rounding=self.product_uom.rounding)
            > 0
        ):
            qty += self.qty_multiple - remainder

        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            return procure_recommended_qty

        qty -= op_qtys[self.id]
        qty_rounded = float_round(qty, precision_rounding=self.product_uom.rounding)
        if qty_rounded > 0:
            procure_recommended_qty = qty_rounded
        return procure_recommended_qty

    @api.depends("product_min_qty", "product_id", "qty_multiple")
    def _compute_procure_recommended(self):
        # '_quantity_in_progress' override in 'purchase_stock' method has not
        # been designed to work with NewIds (resulting in KeyError exceptions).
        # To circumvent this, we knowingly skip such records here.
        op_qtys = self.filtered(lambda x: x.id)._quantity_in_progress()
        for op in self:
            if not op.id:
                op.update(
                    {
                        "procure_recommended_qty": False,
                        "procure_recommended_date": False,
                    }
                )
                continue
            qty = 0.0
            virtual_qty = op.with_context(
                location=op.location_id.id
            ).product_id.virtual_available
            if (
                float_compare(
                    virtual_qty,
                    op.product_min_qty,
                    precision_rounding=op.product_uom.rounding or 0.01,
                )
                < 0
            ):
                qty = op._get_procure_recommended_qty(virtual_qty, op_qtys)
            op.procure_recommended_qty = qty
            op.procure_recommended_date = op.lead_days_date
