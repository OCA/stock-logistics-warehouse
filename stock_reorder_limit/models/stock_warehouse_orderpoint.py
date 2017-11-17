# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import math

from openerp import api, fields, models, _
from openerp.tools import float_round
import openerp.addons.decimal_precision as dp


_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Limit search for processing order point procurement.

        When running scheduler with minimum stock rules, do not order for
        products that are inactive or obsolete, except to provide for
        existing orders.
        """
        stock_rules = super(StockWarehouseOrderpoint, self).search(
            args, offset=offset, limit=limit, order=order, count=count)
        if not self.env.context.get('processing_minimum_stock_rules', False):
            return stock_rules
        filtered_stock_rules = stock_rules.filtered(
            lambda r: r.limit_procurement_qty > 0.0)
        not_used = len(stock_rules) - len(filtered_stock_rules)
        if not_used > 0:
            _logger.info(
                _("%d Minimum stock rules are not used for creating"
                  " procurements.") % not_used)
        return filtered_stock_rules

    @api.multi
    def _compute_limit_procurement_qty(self):
        """Limit quantity that can be procured. Normally this is the
        maximum quantity. But for obsolete or inactive products it will
        just be enough to satisfy outstanding orders.

        If purchase has been disabled, procurement will be limited to 0.0,
        unless we manufacture the product ourselves.
        """
        product_model = self.env['product.product']
        mrp_installed = hasattr(product_model, 'bom_count')
        for this in self:
            product = this.product_id
            if not product.purchase_ok and \
                    (not mrp_installed or product.bom_count == 0):
                # Never purchase products, if that is not ok:
                this.limit_procurement_qty = 0.0
                continue
            if product.active and product.state != 'obsolete':
                # Normal max quantity applies:
                this.limit_procurement_qty = this.product_max_qty
                continue
            if this.virtual_location_qty >= 0.0:
                # Still enough to satisfy outstanding sales if any:
                this.limit_procurement_qty = 0.0
                continue
            # If we get here, we still have to procure inactive or
            # obsolete products to satisfy outstanding sales:
            limit_qty = - this.virtual_location_qty
            qty_multiple = this.qty_multiple
            if limit_qty <= qty_multiple:
                this.limit_procurement_qty = qty_multiple
                continue
            # We have to make sure limit_qty is a
            # multiple of qty_multiple:
            divresult = limit_qty / qty_multiple
            if divresult == math.floor(divresult):
                this.limit_procurement_qty = limit_qty
                continue
            this.limit_procurement_qty = float_round(
                (math.floor(divresult) + 1) * qty_multiple,
                precision_rounding=this.product_uom.rounding)

    limit_procurement_qty = fields.Float(
        string='Maximum quantity still to procure',
        compute='_compute_limit_procurement_qty',
        digits=dp.get_precision('Product Unit of Measure'))
    product_state = fields.Selection(
        related='product_id.product_tmpl_id.state',
        readonly=True)
    product_active = fields.Boolean(
        related='product_id.product_tmpl_id.active',
        readonly=True)
    product_purchase_ok = fields.Boolean(
        related='product_id.product_tmpl_id.purchase_ok',
        readonly=True)
