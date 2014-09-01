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

from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def open_stock_reservation(self):
        assert len(self._ids) == 1, "Expected 1 ID, got %r" % self._ids
        data_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        ref = 'stock_reserve.action_stock_reservation'
        action = data_obj.xmlid_to_object(ref)
        action_dict = action.read()
        action_dict['context'] = {
            'search_default_draft': 1,
            'search_default_reserved': 1,
            'default_product_id': self._ids[0],
            'search_default_product_id': self._ids[0]}
        return action
