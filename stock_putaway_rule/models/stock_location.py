# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'location_in_id',
                                       'Putaway Rules')

    def get_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        current_location = self
        putaway_location = self.env['stock.location']
        while current_location and not putaway_location:
            # Looking for a putaway about the product.
            putaway_rules = self.putaway_rule_ids.filtered(lambda x: x.product_id == product)
            if putaway_rules:
                putaway_location = putaway_rules[0].location_out_id
            # If not product putaway found, we're looking with category so.
            else:
                categ = product.categ_id
                while categ:
                    putaway_rules = self.putaway_rule_ids.filtered(lambda x: x.category_id == categ)
                    if putaway_rules:
                        putaway_location = putaway_rules[0].location_out_id
                        break
                    categ = categ.parent_id
            current_location = current_location.location_id
        return putaway_location
