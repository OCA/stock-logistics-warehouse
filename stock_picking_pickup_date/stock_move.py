# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _get_pickup_date(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute(
            """
            SELECT sm.id, sp.pickup_date
            FROM stock_move sm
            LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
            WHERE sm.id IN %s""",
            (tuple(ids), )
        )
        return dict(
            (id, date or False)
            for (id, date) in cr.fetchall()
        )

    def _get_moves_from_picking(self, cr, uid, ids, context=None):
        return self.pool['stock.move'].search(
            cr, uid, [('picking_id', 'in', tuple(ids))], context=context)

    _columns = {
        'pickup_date': fields.function(
            _get_pickup_date, type="datetime", string="Pickup Date",
            store={
                "stock.move": (
                    lambda self, cr, uid, ids, context=None: ids,
                    ['picking_id'], 10),
                "stock.picking": (_get_moves_from_picking,
                                  ['pickup_date'], 10),
                "stock.picking.out": (_get_moves_from_picking,
                                      ['pickup_date'], 10),
                "stock.picking.in": (_get_moves_from_picking,
                                     ['pickup_date'], 10),
            },
        ),
    }
