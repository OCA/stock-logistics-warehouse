# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    force_inventory_date = fields.Boolean(
        help="Force the inventory moves and accounting entries to a given date"
             "in the past.",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.onchange('date')
    def _onchange_force_inventory_date(self):
        if self.force_inventory_date:
            self.accounting_date = self.date.date()

    @api.multi
    def write(self, vals):
        """For inventories with `force_inventory_date` we only allow to
        change `date` if they are in draft and not being confirmed."""
        force_date = self.filtered(lambda l: l.force_inventory_date)
        if not force_date or not vals.get('date'):
            return super().write(vals)
        res = super(StockInventory, self - force_date).write(vals)
        if vals.get('state'):
            vals.pop('date')
            res &= super(StockInventory, force_date).write(vals)
        else:
            draft = force_date.filtered(lambda i: i.state == 'draft')
            res &= super(StockInventory, draft).write(vals)
            vals.pop('date')
            res &= super(StockInventory, force_date - draft).write(vals)
        return res

    @api.multi
    def _generate_lines_at_date(self, location, product_ids):
        lines = []
        products_at_date = self.env['product.product'].with_context({
            'to_date': self.date,
            'location': location.id,
            'compute_child': False,
        }).search([('id', 'in', product_ids)]).filtered(
            lambda p: p.qty_available)
        for p in products_at_date:
            line = {
                'product_id': p.id,
                'product_qty': p.qty_available,
                'location_id': location.id,
            }
            lines.append(line)
        return lines

    def _get_inventory_lines_values(self):
        if not self.force_inventory_date:
            return super()._get_inventory_lines_values()
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        lines = []
        if self.filter == 'none':
            for loc in locations:
                # To improve performance, we only considered product
                # moved in/out of the location any time in history:
                products = self.env['stock.move'].read_group([
                    '|',
                    ('location_id', '=', loc.id),
                    ('location_dest_id', '=', loc.id),
                    ('product_id.type', '=', 'product'),
                    ('state', '=', 'done'),
                ], ['product_id'], ['product_id'])
                product_ids = [x['product_id'][0] for x in products]

                if product_ids:
                    lines.extend(self._generate_lines_at_date(loc,
                                                              product_ids))

        elif self.filter == 'product':
            for loc in locations:
                lines.extend(self._generate_lines_at_date(
                    loc, self.product_id.ids))
        elif self.filter == 'category':
            product_ids = self.env['product.product'].search([
                ('category_id', '=', self.category_id.id)]).ids
            for loc in locations:
                lines.extend(self._generate_lines_at_date(loc, product_ids))
        else:
            raise ValidationError(_(
                'Option %s not available when forcing Inventory Date.',
                self.filter))
        return lines

    @api.multi
    def post_inventory(self):
        forced_inventories = self.filtered(
            lambda inventory: inventory.force_inventory_date)
        for inventory in forced_inventories:
            lock_date = fields.Date.from_string(
                inventory.company_id.force_inventory_lock_date)
            inventory_date = fields.Datetime.from_string(inventory.date).date()
            if lock_date and inventory_date < lock_date:
                raise ValidationError(_(
                    'It is not possible to force an inventory adjustment to '
                    'a date before %s') % lock_date)
            super(StockInventory, inventory.with_context(
                forced_inventory_date=inventory.date)).post_inventory()
        other_inventories = self - forced_inventories
        if other_inventories:
            super(StockInventory, other_inventories).post_inventory()
