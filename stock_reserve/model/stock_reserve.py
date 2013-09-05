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


from openerp.osv import orm, fields


class stock_reservation(orm.Model):
    """ Allow to reserve products.
    """
    _name = 'stock.reservation'
    _description = 'Stock Reservation'
    _inherits = {'stock.move': 'move_id'}

    _columns = {
        'move_id': fields.many2one('stock.move',
                                   'Reservation Move',
                                   required=True,
                                   readonly=True,
                                   ondelete='cascade',
                                   select=1),
        'date_validity': fields.date('Validity Date'),
    }

    _defaults = {
        'type': 'internal',
    }

    def _get_reservation_location(self, cr, uid, product_id, context=None):
        """ Returns the appropriate destination location to
        reserve a product
        """
        return 1

    def reserve(self, cr, uid, ids, context=None):
        """ Confirm a reservation

        The reservation is done using the default UOM of the product.
        A date until which the product is reserved can be specified.
        """
        move_obj = self.pool.get('stock.move')
        reservations = self.browse(cr, uid, ids, context=context)
        move_ids = [reserv.move_id.id for reserv in reservations]
        move_obj.write(cr, uid, move_ids,
                       {'date_expected': fields.datetime.now()},
                       context=context)
        move_obj.action_confirm(cr, uid, move_ids, context=context)
        move_obj.force_assign(cr, uid, move_ids, context=context)
        move_obj.action_done(cr, uid, move_ids, context=context)
        return True

    def release(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        reservations = self.read(cr, uid, ids, ['move_id'],
                                 context=context, load='_classic_write')
        move_obj = self.pool.get('stock.move')
        move_ids = [reserv['move_id'] for reserv in reservations]
        move_obj.action_cancel(cr, uid, move_ids, context=context)
        return True

    def release_validity_exceeded(self, cr, uid, ids=None, context=None):
        """ Release all the reservation having an exceeded validity date """
        domain = [('date_validity', '<', fields.date.today()),
                  ('state', '=', 'done')]
        if ids:
            domain.append(('id', 'in', ids))
        reserv_ids = self.search(cr, uid, domain, context=context)
        self.release(cr, uid, reserv_ids, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """ Release the reservation before the unlink """
        self.release(cr, uid, ids, context=context)
        return super(stock_reservation, self).unlink(cr, uid, ids,
                                                     context=context)

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False, context=None):
        """ On change of product id, if finds UoM, UoS,
        quantity and UoS quantity.
        """
        move_obj = self.pool.get('stock.move')
        if ids:
            reserv = self.read(cr, uid, ids, ['move_id'], context=context,
                               load='_classic_write')
            move_ids = [rv['move_id'] for rv in reserv]
        else:
            move_ids = []
        return move_obj.onchange_product_id(
            cr, uid, move_ids, prod_id=prod_id, loc_id=loc_id,
            loc_dest_id=loc_dest_id, partner_id=partner_id)

    def _get_reservation_location(self, cr, uid, context=None):
        location_obj = self.pool.get('stock.location')
        data_obj = self.pool.get('ir.model.data')
        get_ref = data_obj.get_object_reference
        try:
            __, dest_location_id = get_ref(cr, uid, 'stock_reserve',
                                           'stock_location_reservation')
            location_obj.check_access_rule(cr, uid, [dest_location_id],
                                           'read', context=context)
        except (orm.except_orm, ValueError):
            dest_location_id = False
        return dest_location_id

    def onchange_move_type(self, cr, uid, ids, type, context=None):
        """ On change of move type gives source and destination location.
        """
        move_obj = self.pool.get('stock.move')
        result = move_obj.onchange_move_type(cr, uid, ids, type,
                                             context=context)
        dest_location_id = self._get_reservation_location(cr, uid, context=context)
        result['value']['location_dest_id'] = dest_location_id
        return result

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty, context=None):
        """ On change of product quantity avoid negative quantities """
        if not product_id or product_qty <= 0.0:
            return {'value': {'product_qty': 0.0}}
        return {}
