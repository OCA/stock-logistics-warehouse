# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    actual_date = fields.Date(
        compute="_compute_actual_date",
        store=True,
    )
    actual_date_source = fields.Date(
        help="Technical field to store the actual_date of the source document."
    )

    def _get_timezone(self):
        return self.env.context.get("tz") or self.env.user.tz or "UTC"

    @api.model_create_multi
    def create(self, vals_list):
        # This handles the case where a move is created separately after the parent
        # record.
        # For example, in mrp_stock_actual_date, the actual_date is passed via context
        # when validating an unbuild order or a scrap.
        actual_date_source = self.env.context.get("actual_date_source")
        if actual_date_source:
            for vals in vals_list:
                vals["actual_date_source"] = actual_date_source
        return super().create(vals_list)

    @api.depends("date", "actual_date_source")
    def _compute_actual_date(self):
        tz = self._get_timezone()
        for rec in self:
            if rec.actual_date_source:
                rec.actual_date = rec.actual_date_source
                continue
            rec.actual_date = fields.Date.context_today(
                self.with_context(tz=tz), rec.date
            )

    def _action_done(self, cancel_backorder=False):
        moves = super()._action_done(cancel_backorder)
        # i.e. Inventory adjustments with actual date
        if self.env.context.get("force_period_date"):
            self.write({"actual_date_source": self.env.context["force_period_date"]})
        return moves

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
        actual_date = self.env.context.get("force_period_date") or self.actual_date
        if actual_date:
            am_vals.update({"date": actual_date})
        return am_vals

    def _get_price_unit(self):
        """Passes the actual_date to be used in currency conversion for receipts
        in foreign currency purchases.
        """
        self.ensure_one()
        self = self.with_context(actual_date=self.actual_date)
        return super()._get_price_unit()
