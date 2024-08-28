# Copyright 2024 Matt Taylor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools import float_is_zero


class StockLot(models.Model):
    _inherit = "stock.lot"

    specific_ident_cost = fields.Boolean(
        related="product_id.specific_ident_cost",
        readonly=True,
    )
    value_svl = fields.Float(
        compute="_compute_value_svl",
        compute_sudo=True,
    )
    quantity_svl = fields.Float(
        compute="_compute_value_svl",
        compute_sudo=True,
    )
    avg_cost = fields.Monetary(
        string="Average Cost",
        compute="_compute_value_svl",
        compute_sudo=True,
        currency_field="company_currency_id",
    )
    total_value = fields.Monetary(
        compute="_compute_value_svl",
        compute_sudo=True,
        currency_field="company_currency_id",
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Valuation Currency",
        compute="_compute_value_svl",
        compute_sudo=True,
        help="Technical field to correctly show the currently selected"
        "company's currency that corresponds to the totaled value of the"
        "lot's valuation layers",
    )
    stock_valuation_layer_ids = fields.One2many(
        comodel_name="stock.valuation.layer",
        inverse_name="lot_id",
    )
    valuation = fields.Selection(
        related="product_id.categ_id.property_valuation",
        readonly=True,
    )
    cost_method = fields.Selection(
        related="product_id.categ_id.property_cost_method",
        readonly=True,
    )

    @api.depends("stock_valuation_layer_ids")
    @api.depends_context("to_date", "company")
    def _compute_value_svl(self):
        """Compute totals of multiple svl related values"""
        company_id = self.env.company
        self.company_currency_id = company_id.currency_id
        domain = [
            ("lot_id", "in", self.ids),
            ("company_id", "=", company_id.id),
        ]
        if self.env.context.get("to_date"):
            to_date = fields.Datetime.to_datetime(self.env.context["to_date"])
            domain.append(("create_date", "<=", to_date))
        groups = self.env["stock.valuation.layer"]._read_group(
            domain=domain,
            fields=["product_id:array_agg", "value:sum", "quantity:sum"],
            groupby=["lot_id", "product_id"],
        )
        lots = self.browse()

        # Browse all products and compute products' quantities_dict in batch.
        # This is a fast way of updating the computed quantities
        self.env["product.product"].browse(
            [group["product_id"][0] for group in groups]
        ).sudo(False).mapped("qty_available")

        for group in groups:
            lot = self.browse(group["lot_id"][0])
            value_svl = company_id.currency_id.round(group["value"])
            avg_cost = value_svl / group["quantity"] if group["quantity"] else 0
            lot.value_svl = value_svl
            lot.quantity_svl = group["quantity"]
            lot.avg_cost = avg_cost
            lot.total_value = avg_cost * lot.sudo(False).product_qty
            lots |= lot
        remaining = self - lots
        remaining.value_svl = 0
        remaining.quantity_svl = 0
        remaining.avg_cost = 0
        remaining.total_value = 0

    def _prepare_out_svl_vals(self, quantity, company):
        """Prepare the values for a stock valuation layer created by a delivery.
        This should only be called for specific identification valuation method.

        :param quantity: the quantity to value, expressed in `product_id.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        self.ensure_one()
        company_id = self.env.context.get("force_company", self.env.company.id)
        company = self.env["res.company"].browse(company_id)
        sid_vals = self._run_out_spec_ident(quantity, company)
        vals = {
            "lot_id": self.id,
            "product_id": self.product_id.id,
            "value": sid_vals.get("value"),
            "unit_cost": sid_vals.get("unit_cost"),
            "quantity": -1 * quantity,  # negative for out valuation layers
            "remaining_qty": sid_vals.get("remaining_qty"),
        }
        return vals

    def _run_out_spec_ident(self, quantity, company):
        self.ensure_one()

        # Find back incoming stock valuation layers (called candidates here) to
        # value `quantity`.
        qty_to_take_on_candidates = quantity
        candidates = (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(
                [
                    ("lot_id", "=", self.id),
                    ("remaining_qty", ">", 0),
                    ("company_id", "=", company.id),
                ]
            )
        )
        new_standard_price = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        for candidate in candidates:
            qty_taken_on_candidate = min(
                qty_to_take_on_candidates, candidate.remaining_qty
            )

            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
            new_standard_price = candidate_unit_cost
            value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
            value_taken_on_candidate = candidate.currency_id.round(
                value_taken_on_candidate
            )
            new_remaining_value = candidate.remaining_value - value_taken_on_candidate

            candidate_vals = {
                "remaining_qty": candidate.remaining_qty - qty_taken_on_candidate,
                "remaining_value": new_remaining_value,
            }

            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate

            if float_is_zero(
                qty_to_take_on_candidates,
                precision_rounding=self.product_id.uom_id.rounding,
            ):
                if float_is_zero(
                    candidate.remaining_qty,
                    precision_rounding=self.product_id.uom_id.rounding,
                ):
                    next_candidates = candidates.filtered(
                        lambda svl: svl.remaining_qty > 0
                    )
                    new_standard_price = (
                        next_candidates
                        and next_candidates[0].unit_cost
                        or new_standard_price
                    )
                break

        # update standard price from the last used candidate
        if new_standard_price:
            self.product_id.sudo().with_company(company.id).with_context(
                disable_auto_svl=True
            ).standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates, we
        # fall in the negative stock use case. We chose to value the out move at
        # the price of the last out and a correction entry will be made once
        # `_fifo_vacuum` is called.
        vals = {}
        if float_is_zero(
            qty_to_take_on_candidates,
            precision_rounding=self.product_id.uom_id.rounding,
        ):
            vals = {
                "value": -tmp_value,
                "unit_cost": tmp_value / quantity,
            }
        else:
            assert qty_to_take_on_candidates > 0
            last_fifo_price = new_standard_price or self.product_id.standard_price
            negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                "remaining_qty": -qty_to_take_on_candidates,
                "value": -tmp_value,
                "unit_cost": last_fifo_price,
            }

        return vals

    def action_revaluation(self):
        self.ensure_one()
        view = self.env.ref(
            "stock_valuation_specific_identification."
            "stock_valuation_layer_lot_revaluation_form_view"
        )
        ctx = dict(
            self._context,
            default_lot_id=self.id,
            default_product_id=self.product_id.id,
            default_company_id=self.env.company.id,
        )
        return {
            "name": _("Lot/Serial Revaluation"),
            "view_mode": "form",
            "res_model": "stock.valuation.layer.lot.revaluation",
            "view_id": view.id,
            "type": "ir.actions.act_window",
            "context": ctx,
            "target": "new",
        }
