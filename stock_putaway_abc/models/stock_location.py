# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    def _get_abc_classification_selection(self):
        return self.env['stock.abc.putaway.strat']._get_abc_priority_selection()

    # TODO Check if we want to define this only on locations without children
    #  or if filtering those in validate_abc_location is enough
    abc_classification = fields.Selection(
        _get_abc_classification_selection(),
    )
