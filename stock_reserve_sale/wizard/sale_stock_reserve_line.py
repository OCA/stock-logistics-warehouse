# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class SaleStockReserveLine(models.TransientModel):
    _name = "sale.stock.reserve.line"
    _description = "Sale Stock Reserve Line"

    wizard_id = fields.Many2one("sale.stock.reserve", required=True, ondelete="cascade")
    sale_line_id = fields.Many2one(
        "sale.order.line", string="Order Line", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one(related="sale_line_id.product_id")
    lot_ids = fields.Many2many(
        "stock.lot",
        string="Lots/Serial Numbers",
        # Set here and not only in the view, as the web client doesn't use the
        # view context when reading the names of the selected lots.
        context={"show_available_qty": True},
    )
    product_uom = fields.Many2one(related="sale_line_id.product_uom")
    product_uom_qty = fields.Float(
        related="sale_line_id.product_uom_qty", string="Ordered Quantity"
    )
    has_tracking = fields.Selection(related="product_id.tracking")
    available_qty = fields.Float(
        string="Available Quantity",
        compute="_compute_available_qty",
        digits="Product Unit of Measure",
    )
    quantity = fields.Float(
        string="Quantity to Reserve",
        compute="_compute_quantity",
        store=True,
        readonly=False,
        digits="Product Unit of Measure",
    )

    @api.depends("wizard_id.location_id", "sale_line_id")
    def _compute_available_qty(self):
        for line in self:
            line.available_qty = line._get_available_quantity()

    @api.depends("wizard_id.location_id", "sale_line_id", "lot_ids")
    def _compute_quantity(self):
        for line in self:
            if line.lot_ids:
                line.quantity = line._get_available_quantity(lots=line.lot_ids)
            else:
                line.quantity = line._get_default_quantity()

    def _get_reservation_policy(self):
        self.ensure_one()
        return self.sale_line_id.order_id.company_id.sale_stock_reservation_policy

    def _get_available_quantity(self, lots=None):
        """Unreserved quantity in the wizard location, in the line UoM.

        If ``lots`` is given, only the quantity of those lots is summed.
        """
        self.ensure_one()
        product = self.product_id
        location = self.wizard_id.location_id
        if not location:
            return 0.0
        if product.type != "product" or location.should_bypass_reservation():
            return self.product_uom_qty
        Quant = self.env["stock.quant"]
        if lots:
            # Inside onchanges lots are new records: use the real ones.
            lots = lots._origin
            available = sum(
                Quant._get_available_quantity(product, location, lot_id=lot)
                for lot in lots
            )
        else:
            available = Quant._get_available_quantity(product, location)
        return product.uom_id._compute_quantity(
            available, self.product_uom, rounding_method="DOWN"
        )

    def _get_default_quantity(self):
        self.ensure_one()
        policy = self._get_reservation_policy()
        quantity = self.product_uom_qty
        if policy == "always":
            return quantity
        available = self._get_available_quantity()
        if (
            float_compare(
                available, quantity, precision_rounding=self.product_uom.rounding
            )
            >= 0
        ):
            return quantity
        if policy == "partial":
            return available
        return 0.0

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            rounding = line.product_uom.rounding
            policy = line._get_reservation_policy()
            if float_compare(line.quantity, 0.0, precision_rounding=rounding) < 0:
                raise ValidationError(
                    _(
                        "The quantity to reserve of %(product)s cannot be negative.",
                        product=line.product_id.display_name,
                    )
                )
            if (
                policy != "always"
                and float_compare(
                    line.quantity, line.available_qty, precision_rounding=rounding
                )
                > 0
            ):
                raise ValidationError(
                    _(
                        "Only %(available)s %(uom)s of %(product)s are available "
                        "in %(location)s.",
                        available=line.available_qty,
                        uom=line.product_uom.name,
                        product=line.product_id.display_name,
                        location=line.wizard_id.location_id.display_name,
                    )
                )
            if (
                policy == "full"
                and not float_is_zero(line.quantity, precision_rounding=rounding)
                and float_compare(
                    line.quantity, line.product_uom_qty, precision_rounding=rounding
                )
                < 0
            ):
                raise ValidationError(
                    _(
                        "Partial reservations are not allowed: reserve the whole "
                        "ordered quantity of %(product)s or nothing.",
                        product=line.product_id.display_name,
                    )
                )
