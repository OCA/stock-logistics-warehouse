# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import fields, models
from odoo.http import request
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = ["sale.order", "stock.lot.catalog.mixin"]
    _name = "sale.order"

    def _stock_lot_is_readonly(self):
        self.ensure_one()
        return self.state == "cancel" or self.locked

    def _get_action_add_from_stock_lot_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_stock_lot_catalog_extra_context(),
            "lot_catalog_currency_id": self.currency_id.id,
            "lot_catalog_digits": self.order_line._fields["price_unit"].get_digits(
                self.env
            ),
        }

    def _get_stock_lot_catalog_order_locations(self):
        """This method retrieves the appropriate locations to use in the
        _get_stock_lot_catalog_order_domain() method and is useful for extending
        functionality in other modules (for example, if you do not want to use
        warehouse_id.lot_stock_id because you want to use all of the
        company's warehouses).
        """
        self.ensure_one()
        return self.warehouse_id.lot_stock_id

    def _get_stock_lot_catalog_order_domain(self):
        extra_domain = [("product_id.sale_ok", "=", True)]
        locations = self._get_stock_lot_catalog_order_locations()
        extra_domain += [("location_id", "child_of", locations.ids)]
        return extra_domain

    def _get_stock_lot_catalog_domain(self):
        extra_domain = self._get_stock_lot_catalog_order_domain()
        return expression.AND([super()._get_stock_lot_catalog_domain(), extra_domain])

    def _get_stock_lot_catalog_record_lines(self, lot_ids, **kwargs):
        grouped_lines = defaultdict(lambda: self.env["sale.order.line"])
        for line in self.order_line.filtered(lambda x: x.lot_id):
            if line.display_type or line.lot_id.id not in lot_ids:
                continue
            grouped_lines[line.lot_id] |= line
        return grouped_lines

    def _get_sol_from_stock_lot_catalog(self, lot_id):
        """This method returns the correct line and allows it to be extended to
        other modules if necessary.
        """
        return self.order_line.filtered(lambda line: line.lot_id.id == lot_id)

    def _prepare_line_vals_from_stock_lot_catalog(self, lot, qty, **kwargs):
        return {
            "order_id": self.id,
            "product_id": lot.product_id.id,
            "product_uom_qty": qty,
            "lot_id": lot.id,
            "sequence": ((self.order_line and self.order_line[-1].sequence + 1) or 10),
        }

    def _update_lot_order_line_info(self, lot_id, quantity, **kwargs):
        """We need our own method instead of using the existing
        _update_order_line_info() because, for example, it is not possible to filter
        by the specific order line we need.
        """
        request.update_context(catalog_skip_tracking=True)
        lot = self.env["stock.lot"].browse(lot_id)
        sol = self._get_sol_from_stock_lot_catalog(lot_id)
        if sol:
            if quantity != 0:
                sol.product_uom_qty = quantity
            elif self.state in ["draft", "sent"]:
                price_unit = self.pricelist_id._get_product_price(
                    product=sol.product_id,
                    quantity=1.0,
                    currency=self.currency_id,
                    date=self.date_order,
                    **kwargs,
                )
                sol.unlink()
                return price_unit
            else:
                sol.product_uom_qty = 0
        elif quantity > 0:
            sol_vals = self._prepare_line_vals_from_stock_lot_catalog(
                lot, quantity, **kwargs
            )
            sol = self.env["sale.order.line"].create(sol_vals)
        else:  # quantity of 0, no line to update, return defaut pricelist price
            return self.pricelist_id._get_product_price(
                product=lot.product_id,
                quantity=1.0,
                currency=self.currency_id,
                date=self.date_order,
                **kwargs,
            )
        return sol._get_discounted_price()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_product_template_attribute_value_ids = fields.Many2many(
        related="lot_id.product_template_attribute_value_ids",
        depends=["lot_id"],
        string="Lot Attribute Values",
    )

    def _get_stock_lot_catalog_lines_data(self, **kwargs):
        product = self.product_id
        res = {
            "quantity": self.product_uom_qty,
            "price": self._get_discounted_price(),
            "readOnly": (
                self.order_id._stock_lot_is_readonly()
                or product.sale_line_warn == "block"
            ),
        }
        if (
            product.sale_line_warn != "no-message"
            and self.productproduct_id.sale_line_warn_msg
        ):
            res["warning"] = product.sale_line_warn_msg
        return res

    def action_add_from_stock_lot_catalog(self):
        order = self.env["sale.order"].browse(self.env.context.get("order_id"))
        return order.action_add_from_stock_lot_catalog()
