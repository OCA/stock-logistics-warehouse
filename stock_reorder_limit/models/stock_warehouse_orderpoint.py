# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import api, fields, models, _
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
            args, offset=offset, limit=limit, order=order, count=count
        )
        if not self.env.context.get('processing_minimum_stock_rules', False):
            return stock_rules
        filtered_stock_rules = stock_rules.filtered(
            lambda r: r.limit_procurement_qty > 0.0
        )
        _logger.info(_(
            "%d Minimum stock rules are not used for creating"
            " procurements."
        ) % (len(stock_rules) - len(filtered_stock_rules)))
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
            this.limit_procurement_qty = this.product_max_qty
            product = this.product_id
            if not product.active or product.state == 'obsolete':
                if this.virtual_location_qty < 0.0:
                    this.limit_procurement_qty = - this.virtual_location_qty
                else:
                    this.limit_procurement_qty = 0.0
            if not product.purchase_ok and \
                    (not mrp_installed or product.bom_count == 0):
                this.limit_procurement_qty = 0.0

    limit_procurement_qty = fields.Float(
        string='Maximum quantity still to procure',
        compute='_compute_limit_procurement_qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_state = fields.Selection(
        related='product_id.product_tmpl_id.state',
        readonly=True,
    )
    product_active = fields.Boolean(
        related='product_id.product_tmpl_id.active',
        readonly=True,
    )
    product_purchase_ok = fields.Boolean(
        related='product_id.product_tmpl_id.purchase_ok',
        readonly=True,
    )
