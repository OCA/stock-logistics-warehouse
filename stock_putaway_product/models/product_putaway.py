# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProductPutaway(models.Model):
    _inherit = 'product.putaway'

    @api.model
    def _get_putaway_options(self):
        ret = super()._get_putaway_options()
        return ret + [('per_product', 'Fixed per product location')]

    product_location_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='putaway_id',
        string='Fixed per product location',
        copy=True,
    )
    method = fields.Selection(
        selection='_get_putaway_options',
    )

    @api.multi
    def get_product_putaway_strategies(self, product):
        """ Get linked product putaway strategy that contains fixed location.
        product.product_putaway_ids is the fasted way to get strategy
        especially when we have thousand of products.
        """
        self.ensure_one()
        strategy = product.product_putaway_ids.filtered(
            lambda strategy: (strategy.putaway_id == self))
        if not strategy:
            strategy = product.product_tmpl_id.product_putaway_ids.filtered(
                lambda strategy: (strategy.putaway_id == self))
        return strategy

    def putaway_apply(self, product):
        """:return a stock.location record or the model."""
        if self.method == 'per_product':
            strategies = self.get_product_putaway_strategies(product)
            strategy = strategies[:1]
            if strategy:
                return strategy.fixed_location_id
        return super().putaway_apply(product)


class StockFixedPutawayStrategy(models.Model):
    _name = 'stock.product.putaway.strategy'
    _rec_name = 'product_product_id'
    _order = 'putaway_id, sequence'

    _sql_constraints = [(
        'putaway_product_location_unique',
        'unique(putaway_id,product_product_id,fixed_location_id)',
        _('There is a duplicate location by put away assignment!')
    )]
    putaway_id = fields.Many2one(
        comodel_name='product.putaway',
        string='Put Away Strategy',
        required=True,
        index=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        index=True,
        oldname='product_template_id',
        required=True,
    )
    product_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        index=True,
    )
    fixed_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        required=True,
        domain=[('usage', '=', 'internal')],
    )
    sequence = fields.Integer()
