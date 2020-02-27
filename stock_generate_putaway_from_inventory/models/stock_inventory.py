# -*- coding: utf-8 -*-
# © 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def _get_putaway_strategy(self):
        if self.putaway_strategy_id:
            return self.putaway_strategy_id
        elif self.location_id:
            return self.location_id._get_putaway_strategy()


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def generate_putaway_strategy(self):
        putaway_locations = {}
        for inventory in self:
            if self.state != 'done':
                raise UserError(_(
                    'Please, validate the stock adjustment before'))
            strategy = self.location_id._get_putaway_strategy()
            if not strategy:
                raise UserError(_(
                    'Please, specify a Putaway Strategy '
                    'on the inventory\'s location (or a parent one)'))
            putaway_locations.update(self._prepare_putaway_locations(strategy))
        for putaway_location in putaway_locations.values():
            putaway_location.pop('qty')
            self.env['stock.product.putaway.strategy'].create(putaway_location)

    def _prepare_putaway_locations(self, strategy):
        self.ensure_one()
        putaway_locations = {}
        for line in self.line_ids:
            if line.product_id.product_putaway_ids:
                continue
            if (line.product_id.id not in putaway_locations
                    or line.product_qty >
                    putaway_locations[line.product_id.id]['qty']):
                # If there is several lines for a product, we will use the
                # one having more products
                putaway_locations[line.product_id.id] = line.\
                    _prepare_putaway_location(strategy)
        return putaway_locations


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    def _prepare_putaway_location(self, strategy):
        self.ensure_one()
        res = {
            'qty': self.product_qty,
            'product_product_id': self.product_id.id,
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'fixed_location_id': self.location_id.id,
            'putaway_id': strategy.id,
        }
        return res
