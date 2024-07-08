# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    product_bom_id = fields.Many2one(
        "product.product",
        string="Product BOM",
        domain="[('bom_ids', '!=', False)]",
        help="Select a product with a BOM to auto-complete stock request lines.",
    )
    quantity_bom = fields.Float(
        string="Quantity BOM",
        help="Specify the quantity for the Product BOM.",
        default=1.0,
    )

    @api.constrains("quantity_bom")
    def _check_quantity_bom(self):
        for order in self:
            if order.quantity_bom <= 0:
                raise ValidationError(_("The quantity BOM must be a positive value."))

    def _prepare_bom_line(self, product, line, line_qty):
        """Prepare a dictionary for a BOM line."""
        return {
            "product_id": product.id,
            "product_uom_id": line.product_uom_id.id,
            "product_uom_qty": line_qty,
            "warehouse_id": self.warehouse_id.id,
            "location_id": self.location_id.id,
            "company_id": self.company_id.id,
            "requested_by": self.requested_by.id,
            "expected_date": self.expected_date,
        }

    def _get_bom_lines_recursive(self, bom, quantity):
        """Recursively fetch BOM lines for a given BOM and quantity."""
        bom_lines = []
        bom_done, lines_done = bom.explode(self.product_bom_id, quantity)
        for line, line_data in lines_done:
            product = line.product_id
            line_qty = line_data["qty"]
            sub_bom = self.env["mrp.bom"]._bom_find(product).get(product)
            if sub_bom:
                # Recursively fetch lines from the sub-BOM
                bom_lines += self._get_bom_lines_recursive(
                    sub_bom, line_qty / sub_bom.product_qty
                )
            else:
                # Add the line directly if no sub-BOM is found
                bom_lines.append(
                    (
                        0,
                        0,
                        self._prepare_bom_line(product, line, line_qty),
                    )
                )
        return bom_lines

    @api.onchange("product_bom_id", "quantity_bom")
    def _onchange_product_bom(self):
        if not self.product_bom_id:
            self.stock_request_ids = [(5, 0, 0)]
            return

        bom = (
            self.env["mrp.bom"]._bom_find(self.product_bom_id).get(self.product_bom_id)
        )
        if not bom:
            raise UserError(_("No BOM found for the selected product."))
        # Clear the existing stock request lines
        self.stock_request_ids = [(5, 0, 0)]
        bom_lines = self._get_bom_lines_recursive(bom, self.quantity_bom)
        self.stock_request_ids = bom_lines
