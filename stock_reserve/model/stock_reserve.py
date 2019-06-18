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

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round

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
    date_validity = fields.Date('Validity Date', default = fields.Date.today)

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
        if not res.get('picking_type_id', None):
            res['picking_type_id'] = self._default_picking_type_id()

        picking_type_id = res.get('picking_type_id')
        if picking_type_id and not res.get('location_id', False):
            picking = self.env['stock.picking'].new(
                {'picking_type_id': picking_type_id})
            picking.onchange_picking_type()
            res['location_id'] = picking.location_id.id
        if 'location_dest_id' in fields_list:
            res['location_dest_id'] = self._default_location_dest_id()
        if 'product_uom_qty' in fields_list:
            res['product_uom_qty'] = 1.0
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
        except ValueError:
            location_id = False
        return location_id

    @api.model
    def _default_picking_type_id(self):
        ref = 'stock.picking_type_out'
        return self.env.ref(ref, raise_if_not_found=False).id

    @api.model
    def _default_location_dest_id(self):
        ref = 'stock_reserve.stock_location_reservation'
        return self.get_location_from_ref(ref)

    @api.multi
    def reserve(self):
        """ Confirm reservations

        The reservation is done using the default UOM of the product.
        A date until which the product is reserved can be specified.
        """
        self.write({'date_expected': fields.Datetime.now()})
        self.mapped('move_id')._action_confirm(merge=False, merge_into=False)
        self.mapped('move_id.picking_id').action_assign()
        return True

    @api.multi
    def release(self):
        """
        Release moves from reservation
        """
        # First we cancel all reserved moves.
        self.mapped('move_id').filtered(
            lambda x: x.state not in ('done', 'draft', 'cancel')
        )._action_cancel()
        # If the move is done, we need to reverse it.
        done_moves = self.mapped('move_id').filtered(lambda x: x.state == 'done')
        # We group them by picking to have one revesed picking for all moves.
        for picking in done_moves.mapped('picking_id'):
            return_obj = self.env['stock.return.picking']
            product_return_moves = []

            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings."))

            for move in done_moves.filtered(lambda x: x.picking_id == picking):
                if move.scrapped:
                    continue

                move_dest_exists = False
                if move.move_dest_ids:
                    move_dest_exists = True

                quantity = move.product_qty - sum(move.move_dest_ids.filtered(
                    lambda m: m.state in [
                        'partially_available', 'assigned', 'done'
                    ]).mapped('move_line_ids').mapped('product_qty')
                )
                quantity = float_round(
                    quantity,
                    precision_rounding=move.product_uom.rounding
                )
                product_return_moves.append(
                    (0, 0, {
                        'product_id': move.product_id.id,
                        'quantity': quantity,
                        'move_id': move.id,
                        'uom_id': move.product_id.uom_id.id
                    }))

            location_id = picking.location_id.id
            if picking.picking_type_id.return_picking_type_id \
                    .default_location_dest_id.return_location:

                location_id = picking.picking_type_id.return_picking_type_id \
                    .default_location_dest_id.id

            parent_location_id = picking.picking_type_id.warehouse_id \
                and picking.picking_type_id.warehouse_id.view_location_id.id \
                or picking.location_id.location_id.id

            wizard = return_obj.create({
                'picking_id': picking.id,
                'location_id': location_id,
                'product_return_moves': product_return_moves,
                'move_dest_exists': move_dest_exists,
                'parent_location_id': parent_location_id,
                'original_location_id': picking.location_id.id,
            })
            wizard._create_returns()
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
        move = self.move_id or self.env['stock.move'].new(
            {'product_id': self.product_id})
        move.onchange_product_id()
        self.name = move.name
        self.product_uom = move.product_uom

    @api.onchange('product_uom_qty')
    def _onchange_quantity(self):
        """ On change of product quantity avoid negative quantities """
        if not self.product_id or self.product_uom_qty <= 0.0:
            self.product_uom_qty = 0.0

    @api.multi
    def open_move(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_action')
        action_dict = action.read()[0]
        action_dict['name'] = _('Reservation Move')
        # open directly in the form view
        view_id = self.env.ref('stock.view_move_form').id
        action_dict.update(
            views=[(view_id, 'form')],
            res_id=self.move_id.id,
            )
        return action_dict
