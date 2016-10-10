# -*- coding: utf-8 -*-
# © 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_tmpl_id',
        string="Product stock locations")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_product_id',
        string="Product stock locations")
