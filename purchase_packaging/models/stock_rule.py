# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        """ add packaging and update product_uom/quantity if necessary
        """
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if not res.get("orderpoint_id", False):
            # if the po line is generated from a procurement (stock rule),
            # store the initial demand
            res["product_qty_needed"] = product_qty
        seller = product_id._select_seller(
            partner_id=values["supplier"].name,
            quantity=res["product_qty"],
            date=po.date_order.date(),
            uom_id=product_id.uom_po_id,
        )
        res["product_purchase_uom_id"] = (
            seller.min_qty_uom_id.id or product_id.uom_po_id.id
        )
        if seller.packaging_id:
            res["packaging_id"] = seller.packaging_id.id
            new_uom_id = seller.product_uom
            if new_uom_id.id != res["product_uom"]:
                res["product_uom"] = new_uom_id
                qty = product_uom._compute_quantity(product_qty, new_uom_id)
                res["product_qty"] = max(qty, seller.min_qty)
        return res

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        res = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        if not line.orderpoint_id:
            # if the po line is generated from a procurement (stock rule)
            # base the computation on what is really needed.
            # eg:
            # 1 product bought by package of 10 units
            # generate a procurement for 5 units
            # -> a po line for 1 pack of 10 units is created
            # generate a second procurement for 5 units
            # without the following code, the po line will be updated to
            # order 2 pack of 10 units which is wrong
            #
            # This code is not needed for orderpoint because in this case,
            # the real need is oncsidered thanks
            # to _quantity_in_progress() method
            product_qty_needed = line.product_qty_needed + product_qty
            res["product_qty_needed"] = product_qty_needed
            res["product_qty"] = product_qty_needed
        return res
