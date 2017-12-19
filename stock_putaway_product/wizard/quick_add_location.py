# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, models, api, fields


class QuickAddProductLocation(models.TransientModel):
    _name = "quick.add.product.location"

    def _default_putaway(self):
        """ Overridable method
        """
        return self.env.ref(
            'stock_putaway_product.product_putaway_per_product_wh',
            raise_if_not_found=False)

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
        products = {}
        for product in self.product_ids:
            products.setdefault(product.product_tmpl_id,
                                self.env['product.product'].browse())
            products[product.product_tmpl_id] |= product
        # Remove existing putaway locations
        self.env['stock.product.putaway.strategy'].search(
            [('putaway_id', '=', self.putaway_id.id),
             ('product_product_id', 'in', self.product_ids._ids)]).unlink()
        for template in products:
            products[template].write({
                'product_putaway_ids': [(0, 0, {
                    'putaway_id': self.putaway_id.id,
                    'product_template_id': template.id,
                    'fixed_location_id': self.fixed_location_id.id})]})
        product_names = ', '.join([x.name for x in self.product_ids])
        return {
            'name': _("Updated products putaway: %s" % product_names),
            'type': 'ir.actions.act_window',
            'res_id': self.env.ref('product.product_normal_action').id,
            'view_mode': 'tree,form',
            'res_model': 'product.product',
        }
