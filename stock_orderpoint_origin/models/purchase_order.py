# Copyright 2021 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_sale_orders(self):
        # Used by action_view_sale_orders, for smart button
        # return self.order_line.sale_order_id
        res = super()._get_sale_orders()
        res |= self.order_line.source_group_ids.sale_id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    source_group_ids = fields.Many2many(
        comodel_name="procurement.group",
        string="Procurements from Forecast Report",
        copy=False,
    )

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        # Store the reorder source Procurement Groups
        # To be used for reference and link navigation
        groups = values.get("source_group_ids")
        if groups:
            vals["source_group_ids"] = [(4, o.id) for o in groups]
        return vals
