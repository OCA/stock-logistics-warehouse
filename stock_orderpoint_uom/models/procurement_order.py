# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        res = super(ProcurementOrder, self)._prepare_orderpoint_procurement(
            orderpoint, product_qty)
        if orderpoint.procure_uom_id:
            res['product_qty'] = orderpoint.procure_uom_id._compute_qty(
                orderpoint.product_id.uom_id.id, product_qty,
                orderpoint.procure_uom_id.id)
            res['product_uom'] = orderpoint.procure_uom_id.id
        return res
