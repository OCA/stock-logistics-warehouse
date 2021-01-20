# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # @override
    @api.model
    def _get_valued_types(self):
        res = super(StockMove, self)._get_valued_types()
        res.append("internal")
        return res

    def _get_internal_move_lines(self):
        self.ensure_one()
        res = self.env["stock.move.line"]
        for move_line in self.move_line_ids:
            if (
                move_line.owner_id
                and move_line.owner_id != move_line.company_id.partner_id
            ):
                continue
            if (
                move_line.location_id._should_be_valued()
                and move_line.location_dest_id._should_be_valued()
            ):
                res |= move_line
        return res

    def _create_internal_svl(self):

        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_internal_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(
                    valued_move_line.qty_done, move.product_id.uom_id
                )
            unit_cost = abs(move._get_price_unit())
            if move.product_id.cost_method == "standard":
                unit_cost = move.product_id.standard_price
            svl_vals = move.product_id._prepare_internal_svl_vals(
                valued_quantity, unit_cost
            )
            svl_vals.update(move._prepare_common_svl_vals())
            svl_vals["description"] = move.picking_id.name
            svl_vals_list.append(svl_vals)
        return self.env["stock.valuation.layer"].sudo().create(svl_vals_list)

    # @override
    def _account_entry_move(self, qty, description, svl_id, cost):
        self.ensure_one()
        res = super()._account_entry_move(qty, description, svl_id, cost)
        if res is not None and not res:
            # `super()` tends to `return False` as an indicator that no
            # valuation should happen in this case
            return res

        # treated by `super()` as a self w/ negative qty due to this hunk:
        # quantity = self.product_qty or context.get('forced_quantity')
        # quantity = quantity if self._is_in() else -quantity
        # so, self qty is flipped twice and thus preserved
        self = self.with_context(forced_quantity=-self.product_qty)

        location_from = self.location_id
        location_to = self.location_dest_id

        # get valuation accounts for product
        if self._is_internal():
            product_valuation_accounts = (
                self.product_id.product_tmpl_id.get_product_accounts()
            )
            stock_valuation = product_valuation_accounts.get("stock_valuation")
            stock_journal = product_valuation_accounts.get("stock_journal")

            if (
                location_from.force_accounting_entries
                and location_to.force_accounting_entries
            ):
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id,
                    qty,
                    description,
                    svl_id,
                    cost,
                )
            elif location_from.force_accounting_entries:
                self._create_account_move_line(
                    location_from.valuation_out_account_id.id,
                    stock_valuation.id,
                    stock_journal.id,
                    qty,
                    description,
                    svl_id,
                    cost,
                )
            elif location_to.force_accounting_entries:
                self._create_account_move_line(
                    stock_valuation.id,
                    location_to.valuation_in_account_id.id,
                    stock_journal.id,
                    qty,
                    description,
                    svl_id,
                    cost,
                )

        return res

    def _is_internal(self):
        self.ensure_one()
        if self._get_internal_move_lines():
            return True
        return False

    def _get_accounting_data_for_valuation(self):
        self.ensure_one()
        (
            journal_id,
            acc_src,
            acc_dest,
            acc_valuation,
        ) = super()._get_accounting_data_for_valuation()
        # intercept account valuation, use account specified on internal
        # location as a local valuation
        if self._is_in() and self.location_dest_id.force_accounting_entries:
            # (acc_src if not dest.usage == 'customer') => acc_valuation
            acc_valuation = self.location_dest_id.valuation_in_account_id.id
        if self._is_out() and self.location_id.force_accounting_entries:
            # acc_valuation => (acc_dest if not dest.usage == 'supplier')
            acc_valuation = self.location_id.valuation_out_account_id.id
        return journal_id, acc_src, acc_dest, acc_valuation
