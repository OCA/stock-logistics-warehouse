# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import api, models, _


_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _procure_orderpoint_confirm(
            self, use_new_cursor=False, company_id=False):
        """Limit search for processing order point procurement."""
        this = self.with_context(processing_minimum_stock_rules=True)
        return super(ProcurementOrder, this)._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id)

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        """Limit procurement to what is sensible."""
        sensible_quantity = min(orderpoint.limit_procurement_qty, product_qty)
        if sensible_quantity < product_qty:
            _logger.info(_(
                "Ordered %.2f of %s, instead of %.2f for orderpoint %s") %
                (sensible_quantity,
                 orderpoint.product_id.name,
                 product_qty,
                 orderpoint.name))
        return super(ProcurementOrder, self)._prepare_orderpoint_procurement(
            orderpoint, sensible_quantity)

    @api.model
    def create(self, vals):
        """Do not create quantity <= 0.0 procurements."""
        if 'product_qty' not in vals or vals['product_qty'] <= 0.0:
            _logger.info(_(
                "No procurement created with quantity 0.0 for"
                " values %s.") % str(vals))
            return self.browse([])
        return super(ProcurementOrder, self).create(vals)
