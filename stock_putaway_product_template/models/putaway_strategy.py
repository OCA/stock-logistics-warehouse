# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>

from odoo import api, fields, models


class PutAwayStrategy(models.Model):
    _inherit = 'product.putaway'

    # Remove product domain to allow to select product templates
    product_location_ids = fields.One2many(domain=[])

    def _get_putaway_rule(self, product):
        return super(PutAwayStrategy, self.with_context(
            filter_putaway_rule=True))._get_putaway_rule(product)


class FixedPutAwayStrategy(models.Model):
    _inherit = "stock.fixed.putaway.strat"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        compute="_compute_product_tmpl_id",
        store=True,
        inverse=lambda self: self,
        ondelete="cascade",
    )

    @api.depends('product_id')
    def _compute_product_tmpl_id(self):
        for rec in self:
            if rec.product_id:
                rec.product_tmpl_id = rec.product_id.product_tmpl_id
            else:
                params = self.env.context.get('params', {})
                if params.get('model', '') == 'product.template':
                    rec.product_tmpl_id = params.get('id', False)

    def filtered(self, func):
        res = super(FixedPutAwayStrategy, self).filtered(func)
        if res or not self.env.context.get('filter_putaway_rule'):
            return res
        product = func.__closure__[0].cell_contents
        if product._name != 'product.product':
            return res
        return self.with_context(filter_putaway_rule=False).filtered(
            lambda x: (x.product_tmpl_id == product.product_tmpl_id and
                       not x.product_id))
