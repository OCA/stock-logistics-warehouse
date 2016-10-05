# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp


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
    method = fields.Selection(selection=_get_putaway_options)


class StockFixedPutawayStrategy(models.Model):
    _name = 'stock.product.putaway.strategy'
    _rec_name = 'product_product_id'
    _order = 'putaway_id, sequence'

    _sql_constraints = [(
        'putaway_product_location_unique',
        'unique(putaway_id,product_product_id,fixed_location_id)',
        _('There is a duplicate location by put away assignment!')
    )]

    @api.model
    def get_default_inventory_id(self):
        return self.env['stock.inventory'].search(
            [('id', '=', self.env.context.get('active_id', False))])

    putaway_id = fields.Many2one(
        comodel_name='product.putaway',
        string='Put Away Strategy',
        required=True,
        index=True)
    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        index=True,
        required=True)
    product_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        index=True)
    fixed_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        required=True,
        domain=[('usage', '=', 'internal')])
    max_qty = fields.Float(
        string='Max Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    sequence = fields.Integer()

    @api.onchange('product_template_id')
    def onchange_product_template_id_(self):
        self.product_product_id = (
            self.product_template_id.product_variant_ids[:1])

    @api.model
    def create(self, vals):
        if not vals.get('product_product_id'):
            vals['product_product_id'] = self.env['product.product'].search(
                [('product_tmpl_id', '=', vals['product_template_id'])],
                limit=1).id
        return super(StockFixedPutawayStrategy, self).create(vals)
