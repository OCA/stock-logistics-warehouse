# Copyright 2016 OdooMRP Team
# Copyright 2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016-17 ForgeFlow, S.L.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    product_location_qty = fields.Float(
        string="Quantity On Location", compute="_compute_product_available_qty"
    )
    incoming_location_qty = fields.Float(
        string="Incoming On Location", compute="_compute_product_available_qty"
    )
    outgoing_location_qty = fields.Float(
        string="Outgoing On Location", compute="_compute_product_available_qty"
    )
    virtual_location_qty = fields.Float(
        string="Forecast On Location", compute="_compute_product_available_qty"
    )
    product_category = fields.Many2one(
        string="Product Category", related="product_id.categ_id", store=True
    )

    def _compute_product_available_qty(self):
        operation_by_locaion = defaultdict(
            lambda: self.env["stock.warehouse.orderpoint"]
        )
        for order in self:
            operation_by_locaion[order.location_id] |= order
        for location_id, order_in_locaion in operation_by_locaion.items():
            products = (
                order_in_locaion.mapped("product_id")
                .with_context(location=location_id.id)
                ._compute_quantities_dict(
                    lot_id=self.env.context.get("lot_id"),
                    owner_id=self.env.context.get("owner_id"),
                    package_id=self.env.context.get("package_id"),
                )
            )
            for order in order_in_locaion:
                product = products[order.product_id.id]
                order.update(
                    {
                        "product_location_qty": product["qty_available"],
                        "incoming_location_qty": product["incoming_qty"],
                        "outgoing_location_qty": product["outgoing_qty"],
                        "virtual_location_qty": product["virtual_available"],
                    }
                )
