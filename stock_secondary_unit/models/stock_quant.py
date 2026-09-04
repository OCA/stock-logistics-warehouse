# Copyright 2025 Quartile (https://wwww.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockQuant(models.Model):
    _inherit = ["stock.quant", "product.secondary.unit.mixin"]
    _name = "stock.quant"
    _secondary_unit_fields = {"qty_field": "quantity", "uom_field": "product_uom_id"}

    secondary_uom_id = fields.Many2one(
        related="product_id.stock_secondary_uom_id",
        store=True,
        default=None,
    )
    # Need precompute=False since secondary_uom_id is not precompute field and we
    # shouldn't depend for compute method of precompute field.
    secondary_uom_qty = fields.Float(precompute=False)
    secondary_uom_inventory_quantity = fields.Float(
        string="Counted Quantity (Secondary Unit)",
        digits="Product Unit of Measure",
        compute="_compute_secondary_uom_inventory_quantity",
        inverse="_inverse_secondary_uom_inventory_quantity",
        help="The product's counted quantity, expressed in the secondary unit. "
        "Filling it in sets the counted quantity accordingly.",
    )
    secondary_uom_dependency_type = fields.Selection(
        related="secondary_uom_id.dependency_type"
    )

    @api.model
    def _get_secondary_uom_qty_depends(self):
        return super()._get_secondary_uom_qty_depends() + ["secondary_uom_id"]

    @api.depends("inventory_quantity", "secondary_uom_id")
    def _compute_secondary_uom_inventory_quantity(self):
        for quant in self:
            if not quant._is_convertible_secondary_uom(quant.secondary_uom_id):
                quant.secondary_uom_inventory_quantity = 0.0
                continue
            quant.secondary_uom_inventory_quantity = (
                quant._convert_qty_to_secondary_uom(quant.inventory_quantity)
            )

    def _inverse_secondary_uom_inventory_quantity(self):
        for quant in self:
            if not quant._is_convertible_secondary_uom(quant.secondary_uom_id):
                continue
            quant.inventory_quantity = self._convert_secondary_uom_qty_to_qty(
                quant.secondary_uom_id,
                quant.secondary_uom_inventory_quantity,
                quant.product_uom_id,
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "secondary_uom_inventory_quantity" not in vals:
                continue
            product = self.env["product.product"].browse(vals.get("product_id"))
            secondary_uom = product.stock_secondary_uom_id
            if not self._is_convertible_secondary_uom(secondary_uom):
                continue
            vals["inventory_quantity"] = self._convert_secondary_uom_qty_to_qty(
                secondary_uom,
                vals.pop("secondary_uom_inventory_quantity"),
                product.uom_id,
            )
        return super().create(vals_list)

    @api.model
    def _get_inventory_fields_write(self):
        return super()._get_inventory_fields_write() + [
            "secondary_uom_inventory_quantity"
        ]

    @api.model
    def _is_convertible_secondary_uom(self, secondary_uom):
        return bool(secondary_uom) and secondary_uom.dependency_type != "independent"

    @api.model
    def _convert_secondary_uom_qty_to_qty(self, secondary_uom, secondary_uom_qty, uom):
        return float_round(
            secondary_uom_qty * secondary_uom.factor, precision_rounding=uom.rounding
        )
