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
    putaway_rule_abc_ids = fields.One2many(
        'stock.putaway.rule.abc', 'location_in_id', 'Putaway Rules'
    )

    def _get_putaway_strategy(self, product):
        location = super()._get_putaway_strategy(product)
        if location:
            return location
        abc_putaway = self._get_putaway_strategy_abc(product)
        if abc_putaway:
            return abc_putaway.find_abc_location()
        return self.env['stock.location']

    def _get_putaway_strategy_abc(self, product):
        current_location = self
        putaway_location = self.env['stock.location']
        while current_location and not putaway_location:
            # Looking for a putaway about the product.
            putaway_rules = self.putaway_rule_abc_ids.filtered(
                lambda x: x.product_id == product)
            if putaway_rules:
                putaway_location = putaway_rules[0].find_abc_location()
            # If not product putaway found, we're looking with category so.
            else:
                categ = product.categ_id
                while categ:
                    putaway_rules = self.putaway_rule_abc_ids.filtered(
                        lambda x: x.category_id == categ)
                    if putaway_rules:
                        putaway_location = putaway_rules[0].find_abc_location()
                        break
                    categ = categ.parent_id
            current_location = current_location.location_id
        return putaway_location
