# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # TODO Display putaway from product.product ?
    #  we probably want to display these if there are no more than one variant

    # TODO Display putaway from product.category
