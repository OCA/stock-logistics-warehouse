# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
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


class StockMove(models.Model):
        _inherit = "stock.move"

        @api.multi
        def action_consume(
                self, product_qty, location_id=False, restrict_lot_id=False,
                restrict_partner_id=False, consumed_for=False):
            res = super(StockMove, self).action_consume(
                product_qty, location_id=location_id, restrict_lot_id=restrict_lot_id,
                restrict_partner_id=restrict_partner_id, consumed_for=consumed_for)
            if 'reserve_stock' in self._context.keys() and self._context['reserve_stock'] == True and consumed_for == False:
                vals = { 
                        'product_id': self.product_id.id,
                        'product_uom': self.product_uom.id,
                        'product_uom_qty': self.product_uom_qty,
                        'name': self.name,
                        'location_id': self.location_dest_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'note': self.note,
                        'product_uos_qty': self.product_uos_qty,
                        'product_uos': self.product_uos.id,
                        'price_unit': self.price_unit,
                        'restrict_partner_id': restrict_partner_id,
                        'restrict_lot_id': restrict_lot_id
                        }
                reserve_stock_obj = self.env['stock.reservation'].create(vals)
                reserve_stock_obj.reserve()
            return res
