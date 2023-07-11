# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
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
    reserves_count = fields.Integer(compute="_compute_reserves_count")
    all_lines_reserved = fields.Boolean(
        compute="_compute_reserves_count", store=True, default=False
    )

    def release_all_stock_reservation(self):
        line_ids = [line.id for order in self for line in order.order_line]
        lines = self.order_line.browse(line_ids)
        lines.release_stock_reservation()
        return True

    def _compute_reserves_count(self):
        reserve_ids = self.env["stock.reservation"]._read_group(
            domain=expression.AND(
                [
                    [("sale_id", "in", self.ids)],
                ]
            ),
            fields=["sale_id"],
            groupby=["sale_id"],
        )
        lines = self.order_line.filtered(
            lambda l: l.product_id.detailed_type != "service"
        )
        for order in self:
            if reserve_ids:
                order.reserves_count = reserve_ids[0]["sale_id_count"]
            else:
                order.reserves_count = 0
            if order.reserves_count == len(lines):
                order.all_lines_reserved = True
            else:
                order.all_lines_reserved = False

    def action_view_reserves_products(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_reserve.action_stock_reservation_tree"
        )
        action["domain"] = [("sale_id", "in", self.ids)]
        action["context"] = {"search_default_groupby_product": False}
        return action

    def action_view_reserves_stock_picking(self):
        stock_picking = ""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        stock_picking = (
            self.env["stock.picking"]
            .search([("origin", "=", self.name)])
            .filtered(lambda a: a.state not in "cancel")
        )
        if stock_picking:
            view_id = self.env.ref("stock.view_picking_form").id
            action.update(views=[(view_id, "form")], res_id=stock_picking.id)
            return action

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
                old_vals["product_uom_qty"],
                float(new_vals["product_uom_qty"]),
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
