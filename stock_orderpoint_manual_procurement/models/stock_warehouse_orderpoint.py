# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil import relativedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round


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
    lead_days = fields.Integer(
        "Lead Time",
        default=1,
        help="Number of days after the orderpoint is triggered to "
        "receive the products or to order to the vendor",
    )
    lead_type = fields.Selection(
        [("net", "Days to get the products"), ("supplier", "Days to purchase")],
        "Lead Type",
        required=True,
        default="supplier",
    )
    allowed_location_ids = fields.One2many(
        comodel_name="stock.location", compute="_compute_allowed_location_ids"
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

    def _get_date_planned(self, product_qty, start_date):
        days = self.lead_days or 0.0
        if self.lead_type == "supplier":
            days += (
                self.product_id._select_seller(
                    quantity=product_qty,
                    date=fields.Date.context_today(self, start_date),
                    uom_id=self.product_uom,
                ).delay
                or 0.0
            )
        date_planned = start_date + relativedelta.relativedelta(days=days)
        return date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.depends("product_min_qty", "product_id", "qty_multiple")
    def _compute_procure_recommended(self):
        op_qtys = self._quantity_in_progress()
        for op in self:
            qty = 0.0
            virtual_qty = op.with_context(
                location=op.location_id.id
            ).product_id.virtual_available
            if (
                float_compare(
                    virtual_qty,
                    op.product_min_qty,
                    precision_rounding=op.product_uom.rounding,
                )
                < 0
            ):
                qty = op._get_procure_recommended_qty(virtual_qty, op_qtys)
            op.procure_recommended_qty = qty
            op.procure_recommended_date = op._get_date_planned(qty, datetime.today())
