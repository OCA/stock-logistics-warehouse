# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Leonardo Pistone
#    Copyright 2013-2015 Camptocamp SA
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


class SaleStockReserve(models.TransientModel):
    _name = 'sale.stock.reserve'

    date_validity = fields.Date(
        "Validity Date",
        help="If a date is given, the reservations will be released "
             "at the end of the validity.")
    note = fields.Text('Notes')

    @api.model
    def _get_so_lines(self):
        model = self.env[self.env.context['active_model']]
        if model._name == 'sale.order':
            lines = model.browse(self.env.context['active_id']).order_line
        elif model._name == 'sale.order.line':
            lines = model.browse(self.env.context['active_ids'])
        else:
            lines = self.env['sale.order.line'].browse()

        return lines

    @api.multi
    def button_reserve(self):
        self.ensure_one()
        close = {'type': 'ir.actions.act_window_close'}
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        if not (active_model and active_ids):
            return close

        lines = self._get_so_lines()
        lines.acquire_stock_reservation(date_validity=self.date_validity,
                                        note=self.note)

        return close
