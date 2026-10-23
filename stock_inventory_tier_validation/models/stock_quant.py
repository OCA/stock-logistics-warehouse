# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class StockQuant(models.Model):
    _inherit = "stock.quant"

    inventory_tier_validation_required = fields.Boolean(
        compute="_compute_inventory_tier_validation_required",
        help="Technical field: a tier definition applies to the inventory "
        "adjustments of this company, so the quantity can only be applied "
        "through a validated adjustment.",
    )

    @api.depends("company_id")
    def _compute_inventory_tier_validation_required(self):
        required = {}
        for quant in self:
            company = quant.company_id
            if company not in required:
                required[company] = self.env[
                    "stock.inventory"
                ]._is_tier_validation_required(company)
            quant.inventory_tier_validation_required = required[company]

    @api.model_create_multi
    def create(self, vals_list):
        quants = super().create(vals_list)
        # Link lines added from the adjustment so that Set to Done applies them
        if self.env.context.get("active_model") == "stock.inventory":
            inventory = self.env["stock.inventory"].browse(
                self.env.context.get("active_id")
            )
            if inventory.state == "in_progress":
                quants.filtered(
                    lambda q: not q.current_inventory_id
                    and q in inventory.stock_quant_ids
                ).current_inventory_id = inventory
        return quants

    def write(self, vals):
        if {"inventory_quantity", "inventory_quantity_set"} & set(vals):
            self._check_inventory_under_validation()
        return super().write(vals)

    def _apply_inventory(self):
        self._check_inventory_tier_validation()
        return super()._apply_inventory()

    def _check_inventory_under_validation(self):
        for quant in self:
            inventory = quant.current_inventory_id
            if (
                inventory.state == "in_progress"
                and inventory.review_ids
                and inventory.validation_status != "rejected"
            ):
                raise UserError(
                    _(
                        "The counted quantities of %(inventory)s are under "
                        "validation. Restart the validation to change them.",
                        inventory=inventory.display_name,
                    )
                )

    def _check_inventory_tier_validation(self):
        for quant in self:
            if (
                quant.current_inventory_id.state == "done"
                or not quant.inventory_tier_validation_required
                or float_is_zero(
                    quant.inventory_diff_quantity,
                    precision_rounding=quant.product_uom_id.rounding,
                )
            ):
                continue
            raise UserError(
                _(
                    "The quantity of %(product)s in %(location)s can only be "
                    "adjusted by setting a validated inventory adjustment to done.",
                    product=quant.product_id.display_name,
                    location=quant.location_id.display_name,
                )
            )
