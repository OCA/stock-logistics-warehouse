# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields, _
from odoo.exceptions import UserError


ABC_SELECTION = [('a', 'A'), ('b', 'B'), ('c', 'C')]


class StockPutawayRuleAbc(models.Model):

    _name = 'stock.putaway.rule.abc'
    _description = 'ABC Chaotic putaway'

    def _default_location_id(self):
        if self.env.context.get('active_model') == 'stock.location':
            return self.env.context.get('active_id')

    product_id = fields.Many2one('product.product', 'Product')
    location_in_id = fields.Many2one(
        'stock.location', 'When product arrives in', check_company=True,
        domain="[('child_ids', '!=', False), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=_default_location_id, required=True, ondelete='cascade')
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
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True
    )

    @api.onchange('location_in_id')
    def _onchange_location_in(self):
        if self.location_out_id:
            child_location_count = self.env['stock.location'].search_count([
                ('id', '=', self.location_out_id.id),
                ('id', 'child_of', self.location_in_id.id),
                ('id', '!=', self.location_in_id.id),
            ])
            if not child_location_count:
                self.location_out_id = None

    def write(self, vals):
        if 'company_id' in vals:
            for rule in self:
                if rule.company_id.id != vals['company_id']:
                    raise UserError(_("Changing the company of this record is forbidden at this point, you should rather archive it and create a new one."))
        return super().write(vals)

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
