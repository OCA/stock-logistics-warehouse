# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        # In this method we need to access the purchase order line quantity
        # to correctly evaluate the forecast.
        # Imagine a product with a minimum rule of 4 units and a purchase
        # multiple of 12. The first run will generate a procurement for 4 Pc
        # but a purchase for 12 units.
        # Let's change the minimum rule to 5 units.
        # The standard subtract_procurements_from_orderpoints will return 4
        # and Odoo will create a procurement for 1 unit which will trigger a
        # purchase of 12 due to the multiple. So the original purchase will
        # be increased to 24 units which is wrong.
        # This override will return 12 and no additionnal procurement will be
        # created
        res = super()._quantity_in_progress()
        domain = [
            ("orderpoint_id", "in", self.ids),
            ("state", "in", ["draft", "sent", "to approve"]),
        ]
        po_lines_read_group_res = self.env["purchase.order.line"].read_group(
            domain=domain,
            fields=["orderpoint_id", "product_qty"],
            groupby=["orderpoint_id"],
        )
        po_lines_dict = {}
        for dic in po_lines_read_group_res:
            orderpoint_id = dic["orderpoint_id"][0]
            qty = dic["product_qty"]
            po_lines_dict[orderpoint_id] = qty
        for orderpoint in self:
            if orderpoint.id in po_lines_dict:
                qty = po_lines_dict[orderpoint.id]
                precision = orderpoint.product_uom.rounding
                if (
                    float_compare(
                        qty, res[orderpoint.id], precision_rounding=precision,
                    )
                    >= 0
                ):
                    res[orderpoint.id] = qty
        return res
