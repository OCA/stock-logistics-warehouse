# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        """ add packaging and update product_uom/quantity if necessary
        """
        self.ensure_one()
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        seller = self.product_id._select_seller(
            partner_id=supplier.name,
            quantity=res['product_qty'],
            date=po.date_order and po.date_order[:10],
            uom_id=self.product_id.uom_po_id)
        if seller.packaging_id:
                res['packaging_id'] = seller.packaging_id.id
                new_uom_id = seller.product_uom
                if new_uom_id.id != res['product_uom']:
                    res['product_uom'] = new_uom_id
                    qty = self.product_uom._compute_quantity(
                        self.product_qty, new_uom_id)
                    res['product_qty'] = max(qty, seller.min_qty)
        return res
