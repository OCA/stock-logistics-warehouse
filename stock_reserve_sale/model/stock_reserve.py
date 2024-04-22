# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockReservation(models.Model):
    _inherit = "stock.reservation"

    sale_line_id = fields.Many2one(
        "sale.order.line", string="Sale Order Line", ondelete="cascade", copy=False
    )
    sale_id = fields.Many2one(
        "sale.order", string="Sale Order", store=True, related="sale_line_id.order_id"
    )

    def release_reserve(self):
        self.update({"sale_line_id": False})
        return super().release_reserve()

    def action_view_reserves_stock_picking_reservation(self):
        stock_picking = self.env["stock.picking"]
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        if self.sale_id:
            stock_picking = self.env["stock.picking"].search(
                [("origin", "=", self.sale_id.name), ("state", "!=", "cancel")], limit=1
            )
        if stock_picking:
            view_id = self.env.ref("stock.view_picking_form").id
            action.update(views=[(view_id, "form")], res_id=stock_picking.id)
        return action
