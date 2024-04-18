# Copyright 2023 Quartile Limited
# Copyright 2023 Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_vals(
        self,
        credit_account_id,
        debit_account_id,
        journal_id,
        qty,
        description,
        svl_id,
        cost,
    ):
        am_vals = super()._prepare_account_move_vals(
            credit_account_id,
            debit_account_id,
            journal_id,
            qty,
            description,
            svl_id,
            cost,
        )
        if self.picking_id.accounting_date:
            am_vals.update({"date": self.picking_id.accounting_date})
        return am_vals

    def _get_price_unit(self):
        """Returns the unit price for the move"""
        self.ensure_one()
        if (
            not self.origin_returned_move_id
            and self.purchase_line_id
            and self.product_id.id == self.purchase_line_id.product_id.id
        ):
            price_unit_prec = self.env["decimal.precision"].precision_get(
                "Product Price"
            )
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                qty = line.product_qty or 1
                price_unit = line.taxes_id.with_context(round=False).compute_all(
                    price_unit, currency=line.order_id.currency_id, quantity=qty
                )["total_void"]
                price_unit = float_round(
                    price_unit / qty, precision_digits=price_unit_prec
                )
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if (
                order.currency_id != order.company_id.currency_id
                and self.picking_id.accounting_date
            ):
                return order.currency_id._convert(
                    price_unit,
                    order.company_id.currency_id,
                    order.company_id,
                    self.picking_id.accounting_date,
                    round=False,
                )
        return super()._get_price_unit()
