# Copyright 2018 Camptocamp SA
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.addons.stock.models.product import OPERATORS
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError

UNIT = dp.get_precision('Product Unit of Measure')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string='Quantity On Hand Unreserved',
        digits=UNIT,
        compute='_compute_product_available_not_res',
        search='_search_quantity_unreserved',
    )

    @api.multi
    @api.depends('product_variant_ids.qty_available_not_res')
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(
                tmpl.mapped('product_variant_ids.qty_available_not_res')
            )

    @api.multi
    def action_open_quants_unreserved(self):
        products_ids = self.mapped('product_variant_ids').ids
        quants = self.env['stock.quant'].search([
            ('product_id', 'in', products_ids),
        ])
        quant_ids = quants.filtered(
            lambda x: x.product_id.qty_available_not_res > 0
        ).ids
        result = self.env.ref('stock.product_open_quants').read()[0]
        result['domain'] = [('id', 'in', quant_ids)]
        result['context'] = {
            'search_default_locationgroup': 1,
            'search_default_internal_loc': 1,
        }
        return result

    def _search_quantity_unreserved(self, operator, value):
        domain = [('qty_available_not_res', operator, value)]
        product_variant_ids = self.env['product.product'].search(domain)
        return [('product_variant_ids', 'in', product_variant_ids.ids)]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_available_not_res = fields.Float(
        string='Qty Available Not Reserved',
        digits=UNIT,
        compute='_compute_qty_available_not_reserved',
        search="_search_quantity_unreserved",
    )

    @api.multi
    def _prepare_domain_available_not_reserved(self):
        domain_quant = [
            ('product_id', 'in', self.ids),
        ]
        domain_quant_locations = self._get_domain_locations()[0]
        domain_quant.extend(domain_quant_locations)
        return domain_quant

    @api.multi
    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_reserved()
        ctx = {'lang': False, 'has_unreserved_quantity': True}
        quants = self.env['stock.quant'].with_context(ctx).read_group(
            domain_quant,
            ['product_id', 'location_id', 'quantity', 'reserved_quantity'],
            ['product_id', 'location_id'],
            lazy=False)
        product_sums = {}
        for quant in quants:
            # create a dictionary with the total value per products
            product_sums.setdefault(quant['product_id'][0], 0.)
            product_sums[quant['product_id'][0]] += (
                quant['quantity'] - quant['reserved_quantity']
            )
        for product in self.with_context(prefetch_fields=False, lang=''):
            available_not_res = float_round(
                product_sums.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding
            )
            res[product.id] = {
                'qty_available_not_res': available_not_res,
            }
        return res

    @api.multi
    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_qty_available_not_reserved(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]['qty_available_not_res']
            prod.qty_available_not_res = qty
        return res

    def _get_domain_locations(self):
        rec = super(ProductProduct, self)._get_domain_locations()
        if self.env.context.get('has_unreserved_quantity', False):
            domain_quant = [
                ('unreserved_quantity', '>', 0.0),
            ]
            rec += (domain_quant,)
        return rec

    def _search_quantity_unreserved(self, operator, value):
        if operator not in OPERATORS:
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)
        if value and operator == '>' and not (
                {'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self.with_context(
                has_unreserved_quantity=True)._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'),
                self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
            return [('id', 'in', product_ids)]
        ids = []
        for product in self.search([]):
            if OPERATORS[operator](product.qty_available_not_res, value):
                ids.append(product.id)
        return [('id', 'in', ids)]
