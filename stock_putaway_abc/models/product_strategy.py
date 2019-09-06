# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields


ABC_SELECTION = [('a', 'A'), ('b', 'B'), ('c', 'C')]


class PutAwayStrategy(models.Model):

    _inherit = 'product.putaway'

    # TODO PR to add this field to odoo core ?
    location_ids = fields.One2many('stock.location', 'putaway_strategy_id')
    product_abc_strategy_ids = fields.One2many(
        'stock.abc.putaway.strat',
        'putaway_id',
        domain=[('product_id', '!=', False)],
        copy=True,
    )
    category_abc_strategy_ids = fields.One2many(
        'stock.abc.putaway.strat',
        'putaway_id',
        domain=[('category_id', '!=', False)],
        copy=True,
    )

    def putaway_apply(self, product):
        location = super().putaway_apply(product)
        if location:
            return location
        abc_putaway = self._get_abc_putaway_rule(product)
        if abc_putaway:
            return abc_putaway.find_abc_location()
        return self.env['stock.location']

    def _get_abc_putaway_rule(self, product):
        if self.product_abc_strategy_ids:
            put_away = self.product_abc_strategy_ids.filtered(
                lambda x: x.product_id == product
            )
            if put_away:
                return put_away[0]
        if self.category_abc_strategy_ids:
            categ = product.categ_id
            while categ:
                put_away = self.category_abc_strategy_ids.filtered(
                    lambda x: x.category_id == categ
                )
                if put_away:
                    return put_away[0]
                categ = categ.parent_id
        return self.env['stock.location']


class ABCPutAwayStrategy(models.Model):

    _name = 'stock.abc.putaway.strat'
    _description = 'ABC Chaotic putaway'

    product_id = fields.Many2one('product.product', 'Product')
    putaway_id = fields.Many2one(
        'product.putaway',
        'Put Away Method',
        required=True
    )
    category_id = fields.Many2one('product.category', 'Product Category')
    abc_priority = fields.Selection(
        ABC_SELECTION,
        string='ABC Priority',
        required=True,
    )
    sequence = fields.Integer(
        'Priority',
        help="Give to the more specialized category, a higher priority to have"
             " them in top of the list."
    )

    @api.model
    def _next_abc_priority(self, priority):
        if priority == 'a':
            return 'b'
        elif priority == 'b':
            return 'c'
        elif priority == 'c':
            return 'a'
        return False

    @api.multi
    def validate_abc_locations(self, locations):
        """Return locations without children or locations, to be inherited to
        add validation rules"""
        self.ensure_one()
        no_children_locations = locations.filtered(lambda l: not l.child_ids)
        return no_children_locations or locations

    @api.multi
    def find_abc_location(self):
        self.ensure_one()
        validated_location = self.env['stock.location']
        parent_locations = self.putaway_id.location_ids
        actual_priority = first_priority = self.abc_priority
        while not validated_location:
            children_locations = self.env['stock.location'].search(
                [
                    ('abc_classification', '=', actual_priority),
                    ('id', 'child_of', parent_locations.ids),
                ]
            )
            if not children_locations:
                actual_priority = self._next_abc_priority(actual_priority)
                # Quit the loop if we went through the 3 priorities without
                # success
                if actual_priority == first_priority:
                    validated_location = self.env['stock.location']
                    break
            else:
                validated_location = self.validate_abc_locations(
                    children_locations
                )[0]
        return validated_location
