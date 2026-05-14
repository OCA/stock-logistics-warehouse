# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields, models

DELTA_MAPPING = {
    "day": "days",
    "week": "weeks",
    "month": "months",
    "year": "years",
}


class StockLot(models.Model):
    _inherit = "stock.lot"

    customer_warranty_start_date = fields.Date(
        string="Customer Warranty Start", tracking=True
    )
    customer_warranty_end_date = fields.Date(
        string="Customer Warranty End", tracking=True
    )

    vendor_warranty_start_date = fields.Date(
        string="Vendor Warranty Start", tracking=True
    )
    vendor_warranty_end_date = fields.Date(string="Vendor Warranty End", tracking=True)

    product_tracking = fields.Selection(related="product_id.tracking")

    def _compute_warranty_end_date(self, start_date, duration, period_type):
        """Compute the warranty end date given a start, duration, and period type."""
        delta = DELTA_MAPPING.get(period_type)
        if not start_date or not duration or not delta:
            return False
        return start_date + relativedelta(**{delta: duration})

    def _set_customer_warranty(self, start_date):
        """Set the customer warranty dates based on the start date and the customer
        warranty duration on the product."""
        self.ensure_one()
        product = self.product_id
        self.customer_warranty_start_date = start_date
        self.customer_warranty_end_date = self._compute_warranty_end_date(
            start_date, product.warranty, product.warranty_type
        )

    def _set_vendor_warranty(self, start_date, vendor, quantity):
        """Set the vendor warranty dates based on the start date and the vendor
        warranty duration on the product."""
        self.ensure_one()
        product = self.product_id
        seller = product._select_seller(
            partner_id=vendor,
            quantity=quantity,
            date=start_date,
        )
        self.vendor_warranty_start_date = start_date
        if seller and seller.warranty_duration:
            self.vendor_warranty_end_date = self._compute_warranty_end_date(
                start_date, seller.warranty_duration, "month"
            )
        else:
            self.vendor_warranty_end_date = False

    def _update_customer_warranty_on_delivery(self, line):
        """Hook called when the lot is delivered to a customer.
        This hook can be overridden by other modules to change warranty logic."""
        # Default behavior: set customer warranty if delivery
        self._set_customer_warranty(
            start_date=line.date.date() or fields.Date.context_today(self)
        )

    def _reset_customer_warranty_on_return(self, line):
        """Hook called when the lot is returned from a customer.
        This hook can be overridden by other modules to change warranty logic."""
        # Default behavior: reset customer warranty if return
        self.customer_warranty_start_date = False
        self.customer_warranty_end_date = False

    def _update_vendor_warranty_on_receipt(self, line):
        """Hook called when the lot is received from a vendor.
        This hook can be overridden by other modules to change warranty logic."""
        # Default behavior: set vendor warranty if receipt
        self._set_vendor_warranty(
            start_date=line.date.date() or fields.Date.context_today(self),
            vendor=line.move_id.partner_id,
            quantity=line.quantity,
        )

    def _reset_vendor_warranty_on_return(self, line):
        """Hook called when the lot is returned to a vendor.
        This hook can be overridden by other modules to change warranty logic."""
        # Default behavior: reset vendor warranty if return
        self.vendor_warranty_start_date = False
        self.vendor_warranty_end_date = False
