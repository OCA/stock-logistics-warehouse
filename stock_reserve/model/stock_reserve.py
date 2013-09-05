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

from datetime import datetime

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FMT


class stock_reservation(orm.Model):
    """ Allow to reserve products.

    A stock reservation is basically a stock move,
    but the reservation is handled by this model using
    a ``_inherits``.
    """
    _name = 'stock.reservation'
    _description = 'Stock Reservation'
    _inherits = {'stock.move': 'move_id'}

    _columns = {
        'move_id': fields.many2one('stock.move',
                                   'Move',
                                   readonly=True,
                                   required=True,
                                   ondelete='cascade',
                                   select=1),
        'date_validity': fields.datetime('Validity Date'),
    }

    def _prepare_reserve(self, cr, uid, product_id, quantity, location_id,
                         date_validity=None, context=None):
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)
        location_dest_id = self._get_reservation_location(
            cr, uid, product_id, context=context)
        vals = {'name': 'Reservation',  # sequence?
                'product_id': product_id,
                'product_qty': quantity,
                'product_uom': product.uom_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'price_unit': product.standard_price or 0.0,
                }
        if date_validity:
            vals.update({'date_validity': date_validity,
                         'date': date_validity,
                         'date_expected': date_validity,
                         })
        else:
            today = datetime.now().strftime(DT_FMT)
            vals.update({'date': today,
                         'date_expected': today,
                         })
        return vals

    def _get_reservation_location(self, cr, uid, product_id, context=None):
        """ Returns the appropriate destination location to
        reserve a product
        """
        return 1

    def reserve(self, cr, uid, product_id, quantity, location_id,
                date_validity=None, context=None):
        """ Reserve a product.

        The reservation is done using the default UOM of the product.
        A date until which the product is reserved can be specified.

        :param product_id: id of the product to reserve
        :param quantity: quantity of products to reserve
        :param location_id: source location for the reservation
        :param date_validity: optional datetime until which the reservation
                              is valid
        :returns: id of the ``stock.reservation`` created
        """
        vals = self._prepare_reserve(cr, uid, product_id, quantity,
                                     location_id,
                                     date_validity=date_validity,
                                     context=context)
        reservation_id = self.create(cr, uid, vals, context=context)
        move_id = self.read(cr, uid,
                            reservation_id,
                            ['move_id'],
                            context=context,
                            load='_classic_write')['move_id']
        move_obj = self.pool.get('stock.move')
        move_obj.action_confirm(cr, uid, [move_id], context=context)
        # TODO: if no quantity in the location, it will stay 'confirmed'
        # after action_confirm(), how to handle that?
        move_obj.action_assign(cr, uid, [move_id])
        return reservation_id

    def release(self, cr, uid, ids, context=None):
        """ Release a reservation """
        return self.unlink(cr, uid, ids, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        reservations = self.read(cr, uid, ids, ['move_id'],
                                 context=context, load='_classic_write')
        move_obj = self.pool.get('stock.move')
        move_ids = [reserv['move_id'] for reserv in reservations]
        move_obj.action_cancel(cr, uid, move_ids, context=context)
        return super(stock_reservation, self).unlink(cr, uid, ids, context=context)
