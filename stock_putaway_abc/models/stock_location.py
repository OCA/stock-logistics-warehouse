# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields
from .product_strategy import ABC_SELECTION

class StockLocation(models.Model):

    _inherit = 'stock.location'

    # TODO Check if we want to define this only on locations without children
    #  or if filtering those in validate_abc_location is enough
    abc_classification = fields.Selection(
        ABC_SELECTION, strinng='ABC Classification'
    )
