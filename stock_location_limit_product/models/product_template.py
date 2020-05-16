# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    equivalent_product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='product_template_equivalence',
        column1='main_product_id',
        column2='equiv_product_id',
        string='Equivalent Products',
        help="Products of equivalent volume to compute the remaining capacity "
             "of an inventory location."
    )
