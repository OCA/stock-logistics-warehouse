# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_round


class StockQuant(models.Model):
    _inherit = "stock.quant"

    vlm_quant_ids = fields.One2many(
        comodel_name="stock.quant.vlm", inverse_name="quant_id"
    )

    def action_view_in_vlm_structure(self):
        """Open the VLM structure filtering by this product to locate it easily"""
        action = self.location_id.action_view_vlm_quants()
        action["domain"] = expression.AND(
            [action["domain"], [("product_id", "=", self.product_id.id)]]
        )
        return action


class StockQuantVlm(models.Model):
    _name = "stock.quant.vlm"
    _inherit = ["vlm.tray.cell.position.mixin"]
    _description = "Vertical Lift Module structure inside the quant"
    _rec_name = "product_id"

    quant_id = fields.Many2one(comodel_name="stock.quant")
    location_id = fields.Many2one(comodel_name="stock.location")
    product_id = fields.Many2one(comodel_name="product.product", required=True)
    tray_id = fields.Many2one(comodel_name="stock.location.vlm.tray")
    tray_type_id = fields.Many2one(related="tray_id.tray_type_id")
    quantity = fields.Float()

    @api.model
    def _is_inventory_mode(self):
        """As in stock.quant inventory mode, we have an special context to trigger
        the update of the linked quant. This way we can make partial stocks tray
        by tray just setting the difference (positive or negative in the quant)"""
        return self.env.context.get("vlm_inventory_mode") and self.user_has_groups(
            "stock.group_stock_manager"
        )

    def _set_inventory_quantity(self, inventory_quantity, skip_diff=None):
        """Update the related quant quantity according to the part of the counted
        quant or tray"""
        if not self._is_inventory_mode():
            return
        for vlm_quant in self.filtered(lambda x: x.product_id.type == "product"):
            rounding = vlm_quant.product_id.uom_id.rounding
            # TODO: Support lots and other quant stuff
            quant = vlm_quant.quant_id or vlm_quant.quant_id.search(
                [
                    ("product_id", "=", vlm_quant.product_id.id),
                    ("location_id", "=", vlm_quant.location_id.id),
                ],
                limit=1,
            )
            quant_quantity = quant.quantity
            diff = float_round(
                inventory_quantity - vlm_quant.quantity, precision_rounding=rounding
            )
            diff_float_compared = float_compare(diff, 0, precision_rounding=rounding)
            # When we create a new record, the diff would be 0
            if skip_diff:
                diff = diff_float_compared = inventory_quantity
            # Update the related quant or create a brand new one
            if diff_float_compared == 0:
                continue
            quant_quantity += diff
            # We want to skip the VLM tasks as we're setting the inventory on hand
            quant = vlm_quant.quant_id.with_context(
                inventory_mode=True, skip_vlm_task=True
            )
            if quant:
                quant.inventory_quantity = quant_quantity
            else:
                vlm_quant.quant_id = quant.create(
                    {
                        "product_id": self.product_id.id,
                        "location_id": self.location_id.id,
                        "inventory_quantity": quant_quantity,
                    }
                )

    def write(self, vals):
        if self._is_inventory_mode() and "quantity" in vals:
            self._set_inventory_quantity(vals["quantity"])
        if "product_id" in vals:
            raise UserError(_("You can't change the product"))
        return super().write(vals)

    @api.model
    def create(self, vals):
        vlm_quant = super().create(vals)
        if self._is_inventory_mode():
            vlm_quant._set_inventory_quantity(vals["quantity"], skip_diff=True)
        return vlm_quant

    def unlink(self):
        """We need to trigger the quantities update whenever this happens"""
        for vlm_quant in self:
            vlm_quant.with_context(vlm_inventory_mode=True).quantity = 0
        return super().unlink()

    def action_task_detail(self):
        return {
            "view_mode": "form",
            "res_model": "stock.quant.vlm",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "context": self._context,
            "target": "new",
        }
