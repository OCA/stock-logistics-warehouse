# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    reservation_count = fields.Float(
        compute='_compute_reservation_count',
        string='# Sales')

    @api.multi
    def _compute_reservation_count(self):
        for product in self:
            product.reservation_count = sum(
                product.product_variant_ids.mapped('reservation_count'))

    @api.multi
    def action_view_reservations(self):
        self.ensure_one()
        ref = 'stock_reserve.action_stock_reservation_tree'
        product_ids = self._get_products()
        action_dict = self._get_act_window_dict(ref)
        action_dict['domain'] = [('product_id', 'in', product_ids)]
        action_dict['context'] = {
            'search_default_draft': 1,
            'search_default_reserved': 1
            }
        return action_dict


class ProductProduct(models.Model):
    _inherit = 'product.product'

    reservation_count = fields.Float(
        compute='_compute_reservation_count',
        string='# Sales')

    @api.multi
    def _compute_reservation_count(self):
        for product in self:
            domain = [('product_id', '=', product.id),
                      ('state', 'in', ['draft', 'assigned'])]
            reservations = self.env['stock.reservation'].search(domain)
            product.reservation_count = sum(reservations.mapped('product_qty'))

    @api.multi
    def action_view_reservations(self):
        self.ensure_one()
        ref = 'stock_reserve.action_stock_reservation_tree'
        action_dict = self.product_tmpl_id._get_act_window_dict(ref)
        action_dict['domain'] = [('product_id', '=', self.id)]
        action_dict['context'] = {
            'search_default_draft': 1,
            'search_default_reserved': 1
            }
        return action_dict
