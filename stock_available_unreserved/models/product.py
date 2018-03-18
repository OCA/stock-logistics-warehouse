# Copyright 2018 Camptocamp SA
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string='Quantity On Hand Unreserved',
        digits=UNIT,
        compute='_compute_product_available_not_res',
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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_available_not_res = fields.Float(
        string='Qty Available Not Reserved',
        digits=UNIT,
        compute='_compute_qty_available_not_reserved',
    )

    @api.multi
    def _product_available_not_res_hook(self, quants):
        """Hook used to introduce possible variations"""
        return False

    @api.multi
    def _prepare_domain_available_not_reserved(self):
        domain_quant = [
            ('product_id', 'in', self.ids),
            ('contains_unreserved', '=', True),
        ]
        domain_quant_locations = self._get_domain_locations()[0]
        domain_quant.extend(domain_quant_locations)
        return domain_quant

    @api.multi
    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_reserved()
        quants = self.env['stock.quant'].with_context(lang=False).search(
            domain_quant,
        )
        # TODO: this should probably be refactored performance-wise
        for prod in self:
            vals = {}
            prod_quant = quants.filtered(lambda x: x.product_id == prod)
            quantity = sum(prod_quant.mapped(
                lambda x: x._get_available_quantity(
                    x.product_id,
                    x.location_id
                )
            ))
            vals['qty_available_not_res'] = quantity
            res[prod.id] = vals
        self._product_available_not_res_hook(quants)

        return res

    @api.multi
    def _compute_qty_available_not_reserved(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]['qty_available_not_res']
            prod.qty_available_not_res = qty
        return res
