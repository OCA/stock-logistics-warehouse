# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        """Limit procurement to what is sensible."""
        sensible_quantity = min(orderpoint.limit_procurement_qty, product_qty)
        return super(ProcurementOrder, self)._prepare_orderpoint_procurement(
            orderpoint, sensible_quantity
        )
