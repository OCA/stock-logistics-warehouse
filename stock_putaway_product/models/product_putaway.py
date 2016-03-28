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
        comodel_name='stock.product.putaway.strat',
        inverse_name='putaway_id',
        string='Fixed per product location',
        copy=True)
    method = fields.Selection(
        selection=_get_putaway_options,
        string="Method",
        required=True)

    @api.model
    def putaway_apply(self, putaway_strat, product):
        if putaway_strat.method == 'per_product':
            strat_domain = [
                ('putaway_id', '=', putaway_strat.id),
                ('product_product_id', '=', product.id),
            ]
            for strat in putaway_strat.product_location_ids.search(
                    strat_domain, limit=1):
                return strat.fixed_location_id.id
        else:
            return super(ProductPutawayStrategy, self).putaway_apply(
                putaway_strat, product)


class FixedPutawayStrat(models.Model):
    _name = 'stock.product.putaway.strat'
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
        sting='Put Away Method',
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
