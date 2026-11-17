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
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        view_id = self.env.ref("stock.view_picking_form").id
        action.update(
            views=[(view_id, "form")],
            view_mode="form",
            res_id=self.picking_id.id,
        )
        return action
