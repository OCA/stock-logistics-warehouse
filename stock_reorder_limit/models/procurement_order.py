# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import api, models, _


_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        """Limit procurement to what is sensible."""
        sensible_quantity = min(orderpoint.limit_procurement_qty, product_qty)
        return super(ProcurementOrder, self)._prepare_orderpoint_procurement(
            orderpoint, sensible_quantity
        )

    @api.model
    def create(self, vals):
        """Do not create quantity <= 0.0 procurements."""
        if 'product_qty' not in vals or vals['product_qty'] <= 0.0:
            _logger.info(_(
                "No procurement created with quantity 0.0 for"
                " values %s.") % str(vals)
            )
            return self.browse([])
        return super(ProcurementOrder, self).create(vals)
