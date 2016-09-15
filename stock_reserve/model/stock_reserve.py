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
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class StockReservation(models.Model):
    """ Allow to reserve products.

    The fields mandatory for the creation of a reservation are:

    * product_id
    * product_uom_qty
    * product_uom
    * name

    The following fields are required but have default values that you may
    want to override:

    * company_id
    * location_id
    * location_dest_id

    Optionally, you may be interested to define:

    * date_validity  (once passed, the reservation will be released)
    * note
    """
    _name = 'stock.reservation'
    _description = 'Stock Reservation'
    _inherits = {'stock.move': 'move_id'}

    move_id = fields.Many2one(
        'stock.move',
        'Reservation Move',
        required=True,
        readonly=True,
        ondelete='cascade',
        index=True)
    date_validity = fields.Date('Validity Date')

    @api.model
    def default_get(self, fields_list):
        """ Fix default values

            - Ensure default value of computed field `product_qty` is not set
              as it would raise an error
            - Compute default `location_id` based on default `picking_type_id`.
              Note: `default_picking_type_id` may be present in context,
              so code that looks for default `location_id` is implemented here,
              because it relies on already calculated default
              `picking_type_id`.
        """
        # if there is 'location_id' field requested, ensure that
        # picking_type_id is also requested, because it is required
        # to compute location_id
        if ('location_id' in fields_list and
                'picking_type_id' not in fields_list):
            fields_list = fields_list + ['picking_type_id']

        res = super(StockReservation, self).default_get(fields_list)

        if 'product_qty' in res:
            del res['product_qty']

        # At this point picking_type_id and location_id
        # should be computed in default way:
        #     1. look up context
        #     2. look up ir_values
        #     3. look up property fields
        #     4. look up field.default
        #     5. delegate to parent model
        #
        # If picking_type_id is present and location_id is not, try to find
        # default value for location_id
        picking_type_id = res.get('picking_type_id', None)
        if picking_type_id and not res.get('location_id', False):
            location = (self.env['stock.picking']
                        .with_context(default_picking_type_id=picking_type_id)
                        ._default_location_source())
            res['location_id'] = getattr(location, 'id', False)
        return res

    @api.model
    def get_location_from_ref(self, ref):
        """ Get a location from a xmlid if allowed
        :param ref: tuple (module, xmlid)
        """
        try:
            location = self.env.ref(ref, raise_if_not_found=True)
            location.check_access_rule('read')
            location_id = location.id
        except (except_orm, ValueError):
            location_id = False
        return location_id

    @api.model
    def _default_picking_type_id(self):
        """ Search for an internal picking type
        """
        type_obj = self.env['stock.picking.type']

        types = type_obj.search([('code', '=', 'internal')], limit=1)
        if types:
            return types[0].id
        return False

    @api.model
    def _default_location_dest_id(self):
        ref = 'stock_reserve.stock_location_reservation'
        return self.get_location_from_ref(ref)

    _defaults = {
        'picking_type_id': _default_picking_type_id,
        'location_dest_id': _default_location_dest_id,
        'product_uom_qty': 1.0,
    }

    @api.multi
    def reserve(self):
        """ Confirm reservations

        The reservation is done using the default UOM of the product.
        A date until which the product is reserved can be specified.
        """
        self.write({'date_expected': fields.Datetime.now()})
        self.mapped('move_id').action_confirm()
        self.mapped('move_id.picking_id').action_assign()
        return True

    @api.multi
    def release(self):
        """
        Release moves from reservation
        """
        self.mapped('move_id').action_cancel()
        return True

    @api.model
    def release_validity_exceeded(self, ids=None):
        """ Release all the reservation having an exceeded validity date """
        domain = [('date_validity', '<', fields.date.today()),
                  ('state', '=', 'assigned')]
        if ids:
            domain.append(('id', 'in', ids))
        self.search(domain).release()
        return True

    @api.multi
    def unlink(self):
        """ Release the reservation before the unlink """
        self.release()
        return super(StockReservation, self).unlink()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ set product_uom and name from product onchange """
        # save value before reading of self.move_id as this last one erase
        # product_id value
        product = self.product_id
        # WARNING this gettattr erase self.product_id
        move = self.move_id
        result = move.onchange_product_id(
            prod_id=product.id, loc_id=False, loc_dest_id=False,
            partner_id=False)
        if result.get('value'):
            vals = result['value']
            # only keep the existing fields on the view
            self.name = vals.get('name')
            self.product_uom = vals.get('product_uom')
            # repeat assignation of product_id so we don't loose it
            self.product_id = product.id

    @api.onchange('product_uom_qty')
    def _onchange_quantity(self):
        """ On change of product quantity avoid negative quantities """
        if not self.product_id or self.product_uom_qty <= 0.0:
            self.product_uom_qty = 0.0

    @api.multi
    def open_move(self):
        self.ensure_one()
        action = self.env.ref('stock.action_move_form2')
        action_dict = action.read()[0]
        action_dict['name'] = _('Reservation Move')
        # open directly in the form view
        view_id = self.env.ref('stock.view_move_form').id
        action_dict.update(
            views=[(view_id, 'form')],
            res_id=self.move_id.id,
            )
        return action_dict
