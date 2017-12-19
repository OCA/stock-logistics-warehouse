# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductPutawayStrategy(models.Model):
    _inherit = 'product.putaway'

    @api.model
    def _get_putaway_options(self):
        ret = super(ProductPutawayStrategy, self)._get_putaway_options()
        return ret + [('per_product', 'Fixed per product location')]

    product_location_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='putaway_id',
        string='Fixed per product location',
        copy=True)
    method = fields.Selection(
        selection=_get_putaway_options,
        string="Method",
        required=True)

    @api.model
    def _get_strategy_domain(self, putaway_strategy, product):
        return [
            ('putaway_id', '=', putaway_strategy.id),
            ('product_product_id', '=', product.id),
        ]

    @api.model
    def putaway_apply(self, putaway_strategy, product):
        if putaway_strategy.method == 'per_product':
            for strategy in putaway_strategy.product_location_ids.search(
                    self._get_strategy_domain(putaway_strategy, product),
                    limit=1):
                return strategy.fixed_location_id.id
        else:
            return super(ProductPutawayStrategy, self).putaway_apply(
                putaway_strategy, product)


class FixedPutawayStrat(models.Model):
    _name = 'stock.product.putaway.strategy'
    _rec_name = 'product_product_id'

    _sql_constraints = [(
        'putaway_product_unique',
        'unique(putaway_id,product_product_id)',
        _('There can only be one fixed location per product!')
    )]

    @api.model
    def get_default_inventory_id(self):
        return self.env['stock.inventory'].search(
            [('id', '=', self.env.context.get('active_id', False))])

    putaway_id = fields.Many2one(
        comodel_name='product.putaway',
        string='Put Away Method',
        required=True,
        select=True)
    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        select=True,
        required=True)
    product_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        required=True,
        select=True,
        domain=[('product_tmpl_id', '=', 'product_template_id.id')])
    fixed_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        required=True,
        domain=[('usage', '=', 'internal')])
