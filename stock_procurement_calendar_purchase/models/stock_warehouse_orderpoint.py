# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import float_compare, float_round

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):

    _name = 'stock.warehouse.orderpoint'
    _inherit = ['stock.warehouse.orderpoint', 'procurement.calendar.mixin']

    _location_field = 'location_id'

    procurement_calendar_id = fields.Many2one(
        'procurement.calendar',
        compute='_compute_calendar_attendance'
    )
    procurement_attendance_id = fields.Many2one(
        'procurement.calendar.attendance',
        compute='_compute_calendar_attendance'
    )
    location_procurement_calendar_id = fields.Many2one(
        'procurement.calendar',
        _compute='_compute_location_procurement_calendar_id'
    )
    scheduled_attendance_date = fields.Datetime(
        compute='_compute_calendar_attendance'
    )
    scheduled_delivery_date = fields.Datetime(
        compute='_compute_calendar_attendance'
    )
    procure_recommended_qty = fields.Float(
        compute='_compute_procure_recommended'
    )
    substract_quantity = fields.Float(
        compute='_compute_procure_recommended'
    )
    expected_seller_id = fields.Many2one(
        'product.supplierinfo',
        string='Expected Supplier',
        compute='_compute_expected_seller_id',
        help="The computed seller at this moment and for the expected "
             "ordering quantities"
    )

    @api.model
    def _get_group(self):
        now_date = datetime.utcnow()
        return [(now_date, None)]

    @api.multi
    def _get_procure_recommended_qty(self, attendance=None):
        """
        We get procure recommended quantity depending on date context.
        As calendar attendances are computed, the context date is computed
        accordingly.
        :param attendance:
        :return: float: quantity
        """
        res = {}
        location_data = defaultdict(
            lambda: dict(products=self.env['product.product'],
                         orderpoints=self.env['stock.warehouse.orderpoint'],
                         groups=list()))
        for orderpoint in self:
            key = (
                orderpoint.location_id.id,
                attendance and attendance.id or None
            )
            location_data[key]['products'] += orderpoint.product_id
            location_data[key]['orderpoints'] += orderpoint
            res[orderpoint.id] = 0.0

        for location_id, location_data in location_data.iteritems():
            location_orderpoints = location_data['orderpoints']
            product_context = dict(self._context,
                                   location=location_orderpoints[
                                       0].location_id.id)

            product_quantity = location_data['products'].with_context(
                product_context)._product_available()
            for orderpoint in location_orderpoints:
                op_product_virtual = \
                    product_quantity[orderpoint.product_id.id][
                        'virtual_available']
                if float_compare(
                        op_product_virtual,
                        orderpoint.product_min_qty,
                        precision_rounding=orderpoint.product_uom.rounding) \
                        <= 0:
                    qty = max(
                        orderpoint.product_min_qty,
                        orderpoint.product_max_qty) - op_product_virtual
                    remainder = orderpoint.qty_multiple > 0 and\
                        qty % orderpoint.qty_multiple or 0.0

                    if float_compare(
                            remainder,
                            0.0,
                            precision_rounding=orderpoint.product_uom.rounding
                    ) > 0:
                        qty += orderpoint.qty_multiple - remainder

                    qty -= orderpoint and not isinstance(
                        orderpoint.id,
                        models.NewId) and orderpoint.substract_quantity or 0.0

                    res[orderpoint.id] = float_round(
                        qty,
                        precision_rounding=orderpoint.product_uom.rounding
                    )
        return res

    @api.multi
    @api.depends('product_id', 'procure_recommended_qty')
    def _compute_expected_seller_id(self):
        for orderpoint in self.filtered(lambda o: o.product_id):
            orderpoint.expected_seller_id = \
                orderpoint.product_id._select_seller(
                    quantity=orderpoint.procure_recommended_qty)

    @api.multi
    @api.depends('product_id', 'location_id', 'product_min_qty',
                 'product_max_qty')
    def _compute_calendar_attendance(self, limit=15):
        """
        We compute here which calendar attendance and which order date
            is applying.
        :param limit:
        :return: N/A
        """
        now = fields.Datetime.now()
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        utc = pytz.utc
        now_as_tz = tz.localize(fields.Datetime.from_string(now))
        now_as_tz = now_as_tz.astimezone(utc)

        orderpoints = self
        domain = self._get_attendances_domain()
        orderpoint_attendances = \
            self.env['procurement.calendar.attendance'].search(
                domain, order="date_from asc")
        product_dependant_calendar_products = orderpoint_attendances.mapped(
            'product_ids')
        i = 0
        procurement_date = fields.Datetime.from_string(now)
        while i <= limit:
            daily_product_attendances, daily_no_product_attendances = \
                self.get_attendances_for_weekday(
                    procurement_date, orderpoint_attendances)
            orderpoints_tmp = orderpoints
            for orderpoint in orderpoints:
                found = False
                order_datetime = False
                # Select only attendance where orderpoint.product is present.
                attendances_to_look_for = daily_product_attendances.filtered(
                    lambda a, ord=orderpoint: ord.product_id in a.product_ids)
                if not attendances_to_look_for:
                    attendances_to_look_for = daily_no_product_attendances
                    if orderpoint.product_id in \
                       product_dependant_calendar_products:
                        # We must skip this day if:
                        # if not product_dependant daily attendances found
                        # for orderpoint BUT
                        # the product is link to a other product_dependant
                        # daily attendances.
                        # That mean an attendance should be found
                        # on the next days.
                        continue
                attendances_with_partner = attendances_to_look_for.filtered(
                    lambda a: a.procurement_calendar_id.partner_id)
                for attendance in attendances_with_partner:
                    order_datetime = attendance.get_datetime_start(
                        att_date=fields.Date.to_string(procurement_date))
                    # skip attendance that have order_datetime lower than now
                    if order_datetime < now_as_tz:
                        continue
                    delivery_attendance = attendance.procurement_attendance_id
                    if delivery_attendance:
                        delivery_date = delivery_attendance.get_datetime_start(
                            att_date=fields.Date.to_string(procurement_date))
                    else:
                        delivery_date = attendance.get_datetime_start(
                            att_date=fields.Date.to_string(procurement_date))
                    # The case we have a partner defined
                    # We don't force partner in _select_seller method as
                    # in procurement, it will select automatically the good
                    # one depending on quantities
                    partner = attendance.procurement_calendar_id.partner_id
                    seller = orderpoint.product_id._select_seller(
                        date=fields.Datetime.to_string(delivery_date),
                        uom_id=orderpoint.product_id.uom_id)
                    if seller.name == partner:
                        orderpoint.procurement_attendance_id = attendance
                        orderpoint.procurement_calendar_id = \
                            attendance.procurement_calendar_id
                        found = attendance
                        break
                if not found:
                    attendances_without_partner = attendances_to_look_for -\
                        attendances_with_partner
                    for attendance in attendances_without_partner:
                        order_datetime = attendance.get_datetime_start(
                            att_date=fields.Date.to_string(procurement_date))
                        # skip attendance that have order_datetime lower
                        # than now
                        if order_datetime < now_as_tz:
                            continue
                        delivery_attendance = \
                            attendance.procurement_attendance_id
                        if delivery_attendance:
                            delivery_date = \
                                delivery_attendance.get_datetime_start(
                                    att_date=fields.Date.to_string(
                                        procurement_date))
                        else:
                            delivery_date = attendance.get_datetime_start(
                                att_date=fields.Date.to_string(
                                    procurement_date))
                        found = attendance
                        break
                if found:
                    orderpoint.scheduled_delivery_date = delivery_date
                    orderpoint.scheduled_attendance_date = order_datetime
                    orderpoints_tmp -= orderpoint
            if not orderpoints_tmp:
                break
            orderpoints = orderpoints_tmp
            procurement_date = procurement_date + relativedelta(days=1)
            i += 1

    @api.multi
    @api.depends('product_id', 'location_id', 'product_min_qty',
                 'product_max_qty', 'procurement_attendance_id')
    def _compute_procure_recommended(self):
        """
        We compute here procure recommended to reorder.
        :param limit:
        :return: N/A
        """
        subtract_procurements = self.subtract_procurements_from_orderpoints()
        for orderpoint in self:
            orderpoint.substract_quantity = subtract_procurements.get(
                orderpoint.id)
            procurement_date = fields.Datetime.from_string(
                orderpoint.scheduled_delivery_date)
            attendance = orderpoint.procurement_attendance_id
            if attendance:
                delivery_attendance = attendance.procurement_attendance_id
                if delivery_attendance:
                    delivery_date = delivery_attendance.get_datetime_start(
                        att_date=fields.Date.to_string(procurement_date))
                else:
                    delivery_date = attendance.get_datetime_start(
                        att_date=fields.Date.to_string(procurement_date))
                # Get expected quantity
                context_delivery = fields.Datetime.to_string(
                    delivery_date)
                procure_recommended_qty = orderpoint.with_context(
                    from_date=context_delivery).\
                    _get_procure_recommended_qty(attendance)
            else:
                # Can't find calendar - considering now
                procurement_date = fields.Datetime.now()
                procure_recommended_qty = orderpoint.with_context(
                    from_date=procurement_date).\
                    _get_procure_recommended_qty()
            orderpoint.procure_recommended_qty =\
                procure_recommended_qty[orderpoint.id]

    @api.multi
    def get_attendances_for_weekday(self, day_dt, attendances):
        """
        Get daily attendance that are:
            - linked to some products
            - not linked to any products
        :param day_dt:
        :param attendances:
        :return: recordset: <procurement.calendar.attendance>
        """
        attendance_obj = self.env['procurement.calendar.attendance']
        daily_product_attendances = attendance_obj
        daily_no_product_attendances = attendance_obj
        weekday = day_dt.weekday()
        day_date = day_dt.date()
        for att in attendances:
            if int(att.dayofweek) == weekday and not \
               (att.date_from and
                fields.Date.from_string(att.date_from) > day_date) and not \
               (att.date_to and fields.Date.from_string(att.date_to) <
               day_date):
                if att.product_ids:
                    daily_product_attendances |= att
                else:
                    daily_no_product_attendances |= att
        return daily_product_attendances, daily_no_product_attendances

    def _get_attendances_domain(self):
        """
        We get either attendances without product dependency or
        if true, we check that the product corresponds
        :return: domain
        """
        product_ids = self.mapped('product_id')
        return expression.OR([
            [('procurement_calendar_id.product_dependant', '=', False)],
            [('product_ids', 'in', product_ids.ids)]
        ])
