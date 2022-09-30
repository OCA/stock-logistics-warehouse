# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    purchase_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        string="Purchase Order Lines",
        copy=False,
        readonly=True,
    )
    purchase_count = fields.Integer(compute="_compute_purchase_count")

    @api.depends("purchase_line_ids")
    def _compute_purchase_count(self):
        for record in self:
            record.purchase_count = len(record.purchase_line_ids.order_id)

    def button_view_purchases(self):
        self.ensure_one()
        orders = self.purchase_line_ids.order_id
        action = self.env["ir.actions.act_window"]._for_xml_id("purchase.purchase_rfq")
        action["display_name"] = _("Generated purchases")
        action["domain"] = [("id", "in", orders.ids)]
        return action
