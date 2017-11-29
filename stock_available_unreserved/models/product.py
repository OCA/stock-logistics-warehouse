# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string='Quantity On Hand Unreserved', digits=UNIT,
        compute='_compute_product_available_not_res')

    qty_available_stock_text = fields.Char(
        compute='_compute_product_available_not_res',
        string='Unreserved stock quantity')

    @api.multi
    @api.depends('product_variant_ids.qty_available_not_res')
    def _compute_product_available_not_res(self):
        no_new = self.filtered(
            lambda x: not isinstance(x.id, models.NewId))
        for tmpl in no_new:
            tmpl.qty_available_not_res = sum(tmpl.mapped(
                'product_variant_ids.qty_available_not_res'))
            tmpl.qty_available_stock_text = "/".join(tmpl.mapped(
                'product_variant_ids.qty_available_stock_text'))

    @api.multi
    def action_open_quants_unreserved(self):
        products = self.mapped('product_variant_ids').ids
        result = self.env.ref('stock.product_open_quants').read()[0]
        result['domain'] = "[('product_id','in',[" + ','.join(
            map(str, products)) + "]), ('reservation_id', '=', False)]"
        result[
            'context'] = "{'search_default_locationgroup': 1, " \
                         "'search_default_internal_loc': 1}"
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_available_not_res = fields.Float(
        string='Qty Available Not Reserved', digits=UNIT,
        compute='_compute_qty_available_not_res')

    qty_available_stock_text = fields.Char(
        compute='_compute_qty_available_not_res', string='Available per stock')

    @api.multi
    def _compute_qty_available_not_res(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]['qty_available_not_res']
            text = res[prod.id]['qty_available_stock_text']
            prod.qty_available_not_res = qty
            prod.qty_available_stock_text = text
        return res

    @api.model
    def _prepare_domain_available_not_res(self, products):
        domain_products = [('product_id', 'in', products.mapped('id'))]
        domain_quant = []
        domain_quant_loc = products._get_domain_locations()[0]

        domain_quant += domain_products

        domain_quant.append(('reservation_id', '=', False))

        domain_quant += domain_quant_loc

        return domain_quant

    @api.multi
    def _product_available_not_res_hook(self, quants):
        """Hook used to introduce possible variations"""
        return False

    @api.multi
    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_res(self)

        quants = self.env['stock.quant'].with_context(lang=False).read_group(
            domain_quant,
            ['product_id', 'location_id', 'qty'],
            ['product_id', 'location_id'],
            lazy=False)
        values_prod = {}
        for quant in quants:
            # create a dictionary with the total value per products
            values_prod.setdefault(quant['product_id'][0], 0)
            values_prod[quant['product_id'][0]] += quant['qty']
        for product in self.with_context(prefetch_fields=False, lang=''):
            res[product.id] = {}
            # get total qty for the product
            qty = float_round(values_prod.get(product.id, 0.0),
                              precision_rounding=product.uom_id.rounding)
            qty_available_not_res = qty
            res[product.id].update({'qty_available_not_res':
                                    qty_available_not_res})
            text = str(qty_available_not_res) + _(" On Hand")
            res[product.id].update({'qty_available_stock_text': text})
        self._product_available_not_res_hook(quants)

        return res
