# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


ABC_SELECTION = [('a', 'A'), ('b', 'B'), ('c', 'C')]


class StockPutawayRule(models.Model):

    _inherit = 'stock.putaway.rule'

    method = fields.Selection(
        [('fixed', 'Fixed location'), ('abc', 'ABC Priority')],
        required=True,
        default='fixed',
    )
    abc_priority = fields.Selection(
        ABC_SELECTION,
        string='ABC Priority',
    )
    location_out_id = fields.Many2one(required=False)

    @api.constrains('method', 'location_out_id', 'abc_priority')
    def _check_method(self):
        for rule in self:
            if rule.method == 'fixed' and not rule.location_out_id:
                raise ValidationError(_(
                    "Fixed putaways require a 'Store to' location."
                ))
            elif rule.method == 'fixed' and rule.abc_priority:
                raise ValidationError(_(
                    "Fixed putaways are not allowed to have an ABC priority."
                ))
            elif rule.method == 'abc' and not rule.abc_priority:
                raise ValidationError(_(
                    "ABC putaways require an ABC priority."
                ))
            elif rule.method == 'abc' and rule.location_out_id:
                raise ValidationError(_(
                    "ABC putaways are not allowed to have a 'Store to' "
                    "location."
                ))

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
        parent_location = self.location_in_id
        actual_priority = first_priority = self.abc_priority
        while not validated_location:
            children_locations = self.env['stock.location'].search(
                [
                    ('abc_classification', '=', actual_priority),
                    ('id', 'child_of', parent_location.id),
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

    def filtered(self, func):
        """Filter putaway strats according to method"""
        putaway_rules = super().filtered(func)
        if self.env.context.get('_putaway_method') == 'fixed':
            filtered_putaways = super(
                StockPutawayRule, putaway_rules
            ).filtered(lambda p: p.method == 'fixed')
            return filtered_putaways
        return putaway_rules
