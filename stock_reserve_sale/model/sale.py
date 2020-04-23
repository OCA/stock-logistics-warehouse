# Copyright 2020 Camptocamp SA.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api, _
from odoo.exceptions import except_orm


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends(
        'state',
        'order_line.reservation_ids', 'order_line.is_stock_reservable')
    def _stock_reservation(self):
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
        compute='_stock_reservation',
        readonly=True,
        multi='stock_reservation',
        store=True,
        string='Has Stock Reservations')
    is_stock_reservable = fields.Boolean(
        compute='_stock_reservation',
        readonly=True,
        multi='stock_reservation',
        store=True,
        string='Can Have Stock Reservations')

    @api.multi
    def release_all_stock_reservation(self):
        line_ids = [line.id for order in self for line in order.order_line]
        lines = self.env['sale.order.line'].browse(line_ids)
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
        product_route_ids = [
            x.id for x in product.route_ids + product.categ_id.total_route_ids]
        rules = ProcurementRule.search([
            ('route_id', 'in', product_route_ids)],
            order='route_sequence, sequence', limit=1)

        if not rules:
            warehouse = self.order_id.warehouse_id
            wh_routes = warehouse.route_ids
            wh_route_ids = [route.id for route in wh_routes]
            domain = [
                '|', ('warehouse_id', '=', warehouse.id),
                ('warehouse_id', '=', False),
                ('route_id', 'in', wh_route_ids)]

            rules = ProcurementRule.search(
                domain, order='route_sequence, sequence')

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
    @api.depends(
        'state', 'product_id.route_ids', 'product_id.type')
    def _is_stock_reservable(self):
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
        compute='_is_stock_reservable',
        readonly=True,
        string='Can be reserved')

    @api.multi
    def release_stock_reservation(self):
        reserv_ids = [
            reserv.id for line in self for reserv in line.reservation_ids]
        reservations = self.env['stock.reservation'].browse(reserv_ids)
        reservations.release()
        return True

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.reservation_ids:
            msg = _(
                "you can't change to new product if old product "
                "has stock reservation")
            msg += "\n\n"
            result.setdefault('warning', {})
            if result['warning'].get('message'):
                result['warning']['message'] += msg
            else:
                result['warning'] = {
                    'title': _('Configuration Error!'),
                    'message': msg,
                }
        return result

    @api.multi
    @api.onchange('product_uom_qty')
    def product_uom_qty_change(self):
        result = {}
        if self.reservation_ids:
            msg = _(
                "As you changed the quantity of the line, "
                "the quantity of the stock reservation will "
                "be automatically adjusted to %.2f.") % self.product_uom_qty
            msg += "\n\n"
            result.setdefault('warning', {})
            if result['warning'].get('message'):
                result['warning']['message'] += msg
            else:
                result['warning'] = {
                    'title': _('Configuration Error!'),
                    'message': msg,
                }
        return result

    @api.multi
    def write(self, vals):
        block_on_reserve = (
            'product_id', 'product_uom', 'type')
        update_on_reserve = (
            'price_unit', 'product_uom_qty')
        keys = set(vals.keys())
        test_block = keys.intersection(block_on_reserve)
        test_update = keys.intersection(update_on_reserve)
        if test_block:
            for line in self:
                if not line.reservation_ids:
                    continue
                raise except_orm(
                    _('Error'),
                    _(
                        'You cannot change the product or unit of measure '
                        'of lines with a stock reservation. '
                        'Release the reservation '
                        'before changing the product.'))
        res = super(SaleOrderLine, self).write(vals)
        if test_update:
            for line in self:
                if not line.reservation_ids:
                    continue
                if len(line.reservation_ids) > 1:
                    raise except_orm(
                        _('Error'),
                        _(
                            'Several stock reservations are linked with the '
                            'line. Impossible to adjust their quantity. '
                            'Please release the reservation '
                            'before changing the quantity.'))
                line.reservation_ids.write({
                    'price_unit': line.price_unit,
                    'product_uom_qty': line.product_uom_qty,
                    })
        return res
