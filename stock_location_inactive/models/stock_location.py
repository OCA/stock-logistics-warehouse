# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare


class StockLocation(orm.Model):

    """
    Subclass stock.location model.

    Extend the model stock.location to add a constraint to check if
    the stock location contains product or is a parent location
    """

    _name = "stock.location"
    _inherit = "stock.location"

    def onchange_active_field(self, cr, uid, ids, active, context=None):
        move_obj = self.pool['stock.move']
        location_obj = self.pool['stock.location']
        if context is None:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]

        if len(ids):
            move_src_ids = move_obj.search(cr, uid, [
                ('location_id', '=', ids[0]),
                ('state', '=', 'done')])
            qty_src = sum([i.product_qty for i in move_obj.browse(
                cr, uid, move_src_ids, context=context)])
            move_dest_ids = move_obj.search(cr, uid, [
                ('location_dest_id', '=', ids[0]),
                ('state', '=', 'done')])
            qty_dest = sum([i.product_qty for i in move_obj.browse(
                cr, uid, move_dest_ids, context=context)])
            location_ids = location_obj.search(
                cr, uid, [('location_id', '=', ids[0]), ('active', '=', True)],
                context=context)
            if not active:
                if len(location_ids) != 0 \
                        or (float_compare(qty_src, qty_dest,
                                          precision_digits=2) != 0):
                    raise orm.except_orm(
                        _('Validation Error'),
                        _('You cannot disable a location that contains '
                          'products or sub-locations')
                    )
        return True

    def write(self, cr, uid, ids, vals, context=None):
        self.onchange_active_field(cr, uid, ids, active=vals.get('active'),
                                   context=context)
        return super(StockLocation, self).write(
            cr, uid, ids, vals, context=context
        )
