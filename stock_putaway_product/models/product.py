# -*- coding: utf-8 -*-

import logging

from openerp import models, fields

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_template_id',
        string="Product stock locations")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_putaway_ids = fields.One2many(
        comodel_name='stock.product.putaway.strategy',
        inverse_name='product_product_id',
        string="Product stock locations")
