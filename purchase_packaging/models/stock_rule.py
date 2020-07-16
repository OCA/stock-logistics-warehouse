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
