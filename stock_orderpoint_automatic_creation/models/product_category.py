# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    create_orderpoints = fields.Selection(
        selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        string='Create Orderpoints',
        company_dependent=True,
    )
