# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError, except_orm
from odoo.tools.translate import _

_LINE_KEYS = ["product_id", "product_uom_qty"]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "state", "order_line.reservation_ids", "order_line.is_stock_reservable"
    )
    def _compute_stock_reservation(self):
        for sale in self:
            has_stock_reservation = False
            is_stock_reservable = False
            for line in sale.order_line:
                if line.reservation_ids:
                    has_stock_reservation = True
                if line.is_stock_reservable:
                    is_stock_reservable = True
            if sale.state not in ("draft", "sent"):
                is_stock_reservable = False
            sale.is_stock_reservable = is_stock_reservable
            sale.has_stock_reservation = has_stock_reservation

    has_stock_reservation = fields.Boolean(
        compute="_compute_stock_reservation",
        readonly=True,
        multi="stock_reservation",
        store=True,
        string="Has Stock Reservations",
    )
    is_stock_reservable = fields.Boolean(
        compute="_compute_stock_reservation",
        readonly=True,
        multi="stock_reservation",
        store=True,
        string="Can Have Stock Reservations",
    )

    def release_all_stock_reservation(self):
        line_ids = [line.id for order in self for line in order.order_line]
        lines = self.env["sale.order.line"].browse(line_ids)
        lines.release_stock_reservation()
        return True

    def action_confirm(self):
        self.release_all_stock_reservation()
        return super().action_confirm()

    def action_cancel(self):
        self.release_all_stock_reservation()
        return super().action_cancel()

    def write(self, vals):
        old_lines = self.mapped("order_line")
        dict_old_lines = {}
        for line in old_lines:
            dict_old_lines[line.id] = {
                "product_id": line.product_id,
                "product_uom_qty": line.product_uom_qty,
            }
        res = super().write(vals)
        for order in self:
            body = ""
            for line in vals.get("order_line", []):
                if line[0] == 1 and list(set(line[2].keys()).intersection(_LINE_KEYS)):
                    body += order.get_message(dict_old_lines.get(line[1]), line[2])
            if body != "":
                order.message_post(body=body)
        return res

    @api.model
    def get_message(self, old_vals, new_vals):
        ProductProduct = self.env["product.product"]
        body = _("<p>Modified Order line data</p>")
        if "product_id" in new_vals:
            old_product = old_vals["product_id"].display_name
            new_product = ProductProduct.browse(new_vals["product_id"]).display_name
            body += _("<div>     <b>Product</b>: ")
            body += "{} → {}</div>".format(old_product, new_product)
        if "product_uom_qty" in new_vals:
            if "product_id" not in new_vals:
                body += _("<div>     <b>Product</b>: %s") % (
                    old_vals["product_id"].display_name
                )
            body += _("<div>     <b>Product qty.</b>: ")
            body += "{} → {}</div>".format(
                old_vals["product_uom_qty"], float(new_vals["product_uom_qty"]),
            )
        body += "<br/>"
        return body

    def unlink(self):
        for order in self:
            if order.has_stock_reservation:
                raise UserError(
                    _(
                        "Sale Order %s has some reserved lines.\n"
                        "Please unreserve this lines before delete the order."
                    )
                    % (order.name)
                )
        return super().unlink()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_line_rule(self):
        """ Get applicable rule for this product

        Reproduce get suitable rule from procurement
        to predict source location """
        StockRule = self.env["stock.rule"]
        product = self.product_id
        product_route_ids = [
            x.id for x in product.route_ids + product.categ_id.total_route_ids
        ]
        rules = StockRule.search(
            [("route_id", "in", product_route_ids)],
            order="route_sequence, sequence",
            limit=1,
        )

        if not rules:
            warehouse = self.order_id.warehouse_id
            wh_routes = warehouse.route_ids
            wh_route_ids = [route.id for route in wh_routes]
            domain = [
                "|",
                ("warehouse_id", "=", warehouse.id),
                ("warehouse_id", "=", False),
                ("route_id", "in", wh_route_ids),
            ]

            rules = StockRule.search(domain, order="route_sequence, sequence")

        if rules:
            fields.first(rules)
        return False

    def _get_procure_method(self):
        """ Get procure_method depending on product routes """
        rule = self._get_line_rule()
        if rule:
            return rule.procure_method
        return False

    @api.depends("state", "product_id.route_ids", "product_id.type")
    def _compute_is_stock_reservable(self):
        for line in self:
            reservable = False
            if (
                not (
                    line.state not in ("draft", "sent")
                    or line._get_procure_method() == "make_to_order"
                    or not line.product_id
                    or line.product_id.type == "service"
                )
                and not line.reservation_ids
            ):
                reservable = True
            line.is_stock_reservable = reservable

    @api.depends("order_id.state", "reservation_ids")
    def _compute_is_readonly(self):
        for line in self:
            line.is_readonly = (
                len(line.reservation_ids) > 0 or line.order_id.state != "draft"
            )

    reservation_ids = fields.One2many(
        "stock.reservation", "sale_line_id", string="Stock Reservation", copy=False
    )
    is_stock_reservable = fields.Boolean(
        compute="_compute_is_stock_reservable", readonly=True, string="Can be reserved"
    )
    is_readonly = fields.Boolean(compute="_compute_is_readonly", store=False)

    def release_stock_reservation(self):
        reserv_ids = [reserv.id for line in self for reserv in line.reservation_ids]
        reservations = self.env["stock.reservation"].browse(reserv_ids)
        reservations.release_reserve()
        return True

    def write(self, vals):
        block_on_reserve = ("product_id", "product_uom", "type")
        update_on_reserve = ("price_unit", "product_uom_qty")
        keys = set(vals.keys())
        test_block = keys.intersection(block_on_reserve)
        test_update = keys.intersection(update_on_reserve)
        if test_block:
            for line in self:
                if not line.reservation_ids:
                    continue
                raise except_orm(
                    _("Error"),
                    _(
                        "You cannot change the product or unit of measure "
                        "of lines with a stock reservation. "
                        "Release the reservation "
                        "before changing the product."
                    ),
                )
        res = super().write(vals)
        if test_update:
            for line in self:
                if not line.reservation_ids:
                    continue
                if len(line.reservation_ids) > 1:
                    raise except_orm(
                        _("Error"),
                        _(
                            "Several stock reservations are linked with the "
                            "line. Impossible to adjust their quantity. "
                            "Please release the reservation "
                            "before changing the quantity."
                        ),
                    )

                line.reservation_ids.write(
                    {
                        "price_unit": line.price_unit,
                        "product_uom_qty": line.product_uom_qty,
                    }
                )
        return res

    def unlink(self):
        for line in self:
            if line.reservation_ids:
                raise UserError(
                    _(
                        'Sale order line "[%s] %s" has a related reservation.\n'
                        "Please unreserve this line before "
                        "delete the line"
                    )
                    % (line.order_id.name, line.name)
                )
        return super().unlink()
