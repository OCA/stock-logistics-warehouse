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
from openerp.exceptions import UserError
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends('state',
                 'order_line.reservation_ids',
                 'order_line.is_stock_reservable')
    def _compute_stock_reservation(self):
        for sale in self:
            has_stock_reservation = False
            is_stock_reservable = False
            for line in sale.order_line:
                if line.reservation_ids:
                    has_stock_reservation = True
                if line.is_stock_reservable:
                    is_stock_reservable = True
            if sale.state not in ('draft', 'sent'):
                is_stock_reservable = False
            sale.is_stock_reservable = is_stock_reservable
            sale.has_stock_reservation = has_stock_reservation

    has_stock_reservation = fields.Boolean(
        compute='_compute_stock_reservation',
        readonly=True,
        store=True,
        string='Has Stock Reservations')
    is_stock_reservable = fields.Boolean(
        compute='_compute_stock_reservation',
        readonly=True,
        store=True,
        string='Can Have Stock Reservations')

    @api.multi
    def release_all_stock_reservation(self):
        lines = self.mapped('order_line')
        lines.release_stock_reservation()
        return True

    @api.multi
    def action_confirm(self):
        self.release_all_stock_reservation()
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_cancel(self):
        self.release_all_stock_reservation()
        return super(SaleOrder, self).action_cancel()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_line_rule(self):
        """ Get applicable rule for this product

        Reproduce get suitable rule from procurement
        to predict source location """
        ProcurementRule = self.env['procurement.rule']
        product = self.product_id
        product_route_ids = (product.route_ids.mapped('id') +
                             product.categ_id.total_route_ids.mapped('id'))
        rules = ProcurementRule.search([('route_id', 'in', product_route_ids)],
                                       order='route_sequence, sequence',
                                       limit=1)

        if not rules:
            warehouse = self.order_id.warehouse_id
            wh_route_ids = warehouse.route_ids.mapped('id')
            domain = ['|', ('warehouse_id', '=', warehouse.id),
                      ('warehouse_id', '=', False),
                      ('route_id', 'in', wh_route_ids)]

            rules = ProcurementRule.search(domain,
                                           order='route_sequence, sequence',
                                           limit=1)

        if rules:
            return rules[0]
        return False

    @api.multi
    def _get_procure_method(self):
        """ Get procure_method depending on product routes """
        rule = self._get_line_rule()
        if rule:
            return rule.procure_method
        return False

    @api.multi
    @api.depends('state',
                 'product_id.route_ids',
                 'product_id.type')
    def _compute_is_stock_reservation(self):
        for line in self:
            reservable = False
            if (not (line.state != 'draft' or
                     line._get_procure_method() == 'make_to_order' or
                     not line.product_id or
                     line.product_id.type == 'service') and
                    not line.reservation_ids):
                reservable = True
            line.is_stock_reservable = reservable

    reservation_ids = fields.One2many(
        'stock.reservation',
        'sale_line_id',
        string='Stock Reservation',
        copy=False)
    is_stock_reservable = fields.Boolean(
        compute='_compute_is_stock_reservation',
        readonly=True,
        string='Can be reserved')

    @api.multi
    def _prepare_stock_reservation(self, date_validity=False, note=False):
        self.ensure_one()

        try:
            owner_id = self.stock_owner_id and self.stock_owner_id.id or False
        except AttributeError:
            owner_id = False
            # module sale_owner_stock_sourcing not installed, fine

        return {'product_id': self.product_id.id,
                'product_uom': self.product_uom.id,
                'product_uom_qty': self.product_uom_qty,
                'date_validity': date_validity,
                'name': "%s (%s)" % (self.order_id.name, self.name),
                'note': note,
                'price_unit': self.price_unit,
                'sale_line_id': self.id,
                'restrict_partner_id': owner_id,
                }

    @api.multi
    def acquire_stock_reservation(self, date_validity=False, note=False):
        reserv_obj = self.env['stock.reservation'].sudo()

        reservations = reserv_obj.browse()
        for line in self:
            if not line.is_stock_reservable:
                continue

            vals = line._prepare_stock_reservation(
                date_validity=date_validity, note=note)

            # Place picking_type_id in context. This is required
            # to make reserve automaticaly find location_id and
            # location_dest_id
            pick_type_id = line.order_id.warehouse_id.int_type_id.id
            reserv_obj_ctx = reserv_obj.with_context(
                default_picking_type_id=pick_type_id)

            reservations |= reserv_obj_ctx.create(vals)
        reservations.reserve()
        return True

    @api.multi
    def release_stock_reservation(self):
        self.mapped('reservation_ids').sudo().release()
        return True

    @api.onchange('product_id', 'product_uom_qty')
    def onchange_product_id_qty(self):
        reserved_qty = sum(self.reservation_ids.mapped('product_uom_qty'))

        precision_digits = dp.get_precision(
            'Product Unit of Measure')(self.env.cr)[1]
        qty_equal = float_compare(
            self.product_uom_qty, reserved_qty,
            precision_digits=precision_digits) == 0.0
        if not qty_equal and self.reservation_ids:
            msg = _("As you changed the quantity of the line, "
                    "the quantity of the stock reservation will "
                    "be automatically adjusted to %.2f."
                    "") % self.product_uom_qty
            return {
                'warning': {
                    'title': _('Configuration Error!'),
                    'message': msg,
                },
            }
        return {}

    @api.multi
    def _update_reservation_price_qty(self):
        for line in self:
            if not line.reservation_ids:
                continue
            if len(line.reservation_ids) > 1:
                raise UserError(
                    _('Several stock reservations are linked with the '
                      'line. Impossible to adjust their quantity. '
                      'Please release the reservation '
                      'before changing the quantity.'))

            line.reservation_ids.sudo().write({
                'price_unit': line.price_unit,
                'product_uom_qty': line.product_uom_qty,
            })

    @api.multi
    def write(self, vals):
        block_on_reserve = ('product_id',
                            'product_uom_id',
                            'type')
        update_on_reserve = ('price_unit',
                             'product_uom_qty',
                             )
        keys = set(vals.keys())
        test_block = keys.intersection(block_on_reserve)
        test_update = keys.intersection(update_on_reserve)
        if test_block and len(self.mapped('reservation_ids')) > 0:
            raise UserError(
                _('You cannot change the product or unit of measure '
                  'of lines with a stock reservation. '
                  'Release the reservation '
                  'before changing the product.'))
        res = super(SaleOrderLine, self).write(vals)
        if test_update:
            self._update_reservation_price_qty()
        return res
