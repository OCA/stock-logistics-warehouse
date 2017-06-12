# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from openerp import _, models, api, fields


class QuickAddProductLocation(models.TransientModel):
    _name = "quick.add.product.location"

    def _default_putaway(self):
        # overridable method
        putaway = self.env.ref(
            'stock_putaway_product.product_putaway_per_product_wh')
        if putaway:
            return putaway.id

    def __default_putaway(self):
        return self._default_putaway()

    putaway_id = fields.Many2one(
        comodel_name='product.putaway', string='Put Away Method',
        required=True, default=__default_putaway)
    fixed_location_id = fields.Many2one(
        comodel_name='stock.location', string='Location', required=True)
    product_ids = fields.Many2many(
        comodel_name='product.product', string='Products', required=True)

    @api.model
    def default_get(self, fields):
        res = super(QuickAddProductLocation, self).default_get(fields)
        product_ids = self.env.context.get('active_ids')
        if product_ids:
            res['product_ids'] = product_ids
        return res

    @api.multi
    def apply_location(self):
        self.ensure_one()
        products = defaultdict(list)
        for product in self.product_ids:
            products[product.product_tmpl_id.id].append(product.id)
        for template_id in products:
            products_with_location = self.env['product.product'].browse(
                products[template_id])
            products_with_location.write({
                'product_putaway_ids': [(0, 0, {
                    'putaway_id': self.putaway_id.id,
                    'product_template_id': template_id,
                    'fixed_location_id': self.fixed_location_id.id})]})
        product_names = ', '.join([x.name for x in self.product_ids])
        return {
            'name': _("Updated Products: %r" % product_names),
            'type': 'ir.actions.act_window',
            'res_id': self.env.ref('product.product_normal_action').id,
            'view_mode': 'tree',
            'res_model': 'product.product',
        }
