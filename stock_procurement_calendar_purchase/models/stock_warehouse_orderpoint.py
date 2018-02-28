# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import float_compare, float_round

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):

    _name = 'stock.warehouse.orderpoint'
    _inherit = ['stock.warehouse.orderpoint', 'procurement.calendar.mixin']

    _location_field = 'location_id'

    procurement_rule_id = fields.Many2one(
        'procurement.rule',
        compute='_compute_procurement_rule_id'
    )
    involved_calendar_ids = fields.Many2many(
        'procurement.calendar',
        compute='_compute_involved_calendar_ids',
        help="The possible involved calendars depending "
        "on product configuration"
    )
    procurement_calendar_id = fields.Many2one(
        'procurement.calendar',
        compute='_compute_procure_recommended'
    )
    procurement_attendance_id = fields.Many2one(
        'procurement.calendar.attendance',
        compute='_compute_procure_recommended'
    )
    location_procurement_calendar_id = fields.Many2one(
        'procurement.calendar',
        _compute='_compute_location_procurement_calendar_id'
    )
    scheduled_attendance_date = fields.Datetime(
        compute='_compute_procure_recommended'
    )
    scheduled_delivery_date = fields.Datetime(
        compute='_compute_procure_recommended'
    )
    procure_recommended_qty = fields.Float(
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
            substract_quantity = location_orderpoints and not isinstance(
                location_orderpoints.id,
                models.NewId) and location_orderpoints.\
                subtract_procurements_from_orderpoints() or 0.0

            product_quantity = location_data['products'].with_context(
                product_context)._product_available()
            for orderpoint in location_orderpoints:
                if not orderpoint.product_id:
                    continue
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
                    qty -= substract_quantity[orderpoint.id]
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
    @api.depends('location_id', 'product_id')
    def _compute_procurement_rule_id(self):
        """
        Compute the procurement rule base on suitable rules
        :return:
        """
        for orderpoint in self:
            vals = {
                'location_id': orderpoint.location_id,
                'product_id': orderpoint.product_id
            }
            virtual_procurement = self.env['procurement.order'].new(vals)
            orderpoint.procurement_rule_id =\
                virtual_procurement._find_suitable_rule()

    @api.multi
    @api.depends('procurement_rule_id')
    def _compute_involved_calendar_ids(self):
        """
        Compute the involved calendars
        :return:
        """
        for orderpoint in self.filtered(
                lambda o: o.procurement_rule_id and
                o.procurement_rule_id.action == 'buy'):
            calendars = self.env['procurement.calendar'].search(
                orderpoint._get_calendar_supplier_domain())
            orderpoint.involved_calendar_ids = calendars

    @api.multi
    @api.depends('product_id', 'location_id', 'product_min_qty',
                 'product_max_qty')
    def _compute_procure_recommended(self, limit=100):
        """
        We compute here which calendar is applying.
        :param limit:
        :return: N/A
        """
        for orderpoint in self:
            procurement_date = fields.Datetime.from_string(
                fields.Datetime.now())
            orderpoint.scheduled_delivery_date = fields.Datetime.now()
            i = 0
            found = False
            while i <= limit:
                attendances = orderpoint.get_attendances_for_weekday(
                    procurement_date,
                    orderpoint.involved_calendar_ids)
                attendances_with_partner = attendances.filtered(
                    lambda a: a.procurement_calendar_id.partner_id)
                context_date = fields.Datetime.to_string(procurement_date)
                attendance = self.env['procurement.calendar.attendance']
                for attendance in attendances_with_partner:
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
                        quantity=orderpoint.procure_recommended_qty,
                        date=fields.Datetime.to_string(delivery_date),
                        uom_id=orderpoint.product_id.uom_id)
                    if seller.name == partner:
                        orderpoint.procurement_attendance_id = attendance
                        orderpoint.procurement_calendar_id = \
                            attendance.procurement_calendar_id
                        # Get expected quantity
                        context_delivery = fields.Datetime.to_string(
                            delivery_date)
                        procure_recommended_qty = orderpoint.with_context(
                            from_date=context_delivery).\
                            _get_procure_recommended_qty(attendance)
                        orderpoint.procure_recommended_qty = \
                            procure_recommended_qty[orderpoint.id]
                        found = True
                        i = limit + 1
                        break
                if found:
                    self._set_procure_dates(
                        orderpoint,
                        attendance,
                        procurement_date,
                        delivery_date
                    )
                attendances_without_partner = attendances -\
                    attendances_with_partner
                for attendance in attendances_without_partner:
                    procure_recommended_qty = orderpoint.with_context(
                        from_date=context_date)._get_procure_recommended_qty(
                        attendance)
                    orderpoint.procure_recommended_qty =\
                        procure_recommended_qty[orderpoint.id]
                    found = True
                    i = limit + 1
                    break
                procurement_date = procurement_date + relativedelta(days=1)
                i += 1
            if not found:
                # Can't find calendar - considering now
                procurement_date = fields.Datetime.now()
                procure_recommended_qty = orderpoint.with_context(
                    from_date=procurement_date)._get_procure_recommended_qty()
                orderpoint.procure_recommended_qty =\
                    procure_recommended_qty[orderpoint.id]

    @api.model
    def _set_procure_dates(
            self, orderpoint, attendance, procurement_date, delivery_date):
        orderpoint.scheduled_delivery_date = delivery_date
        order_date = attendance.get_datetime_start(
            att_date=fields.Date.to_string(procurement_date))
        orderpoint.scheduled_attendance_date = order_date

    @api.multi
    def get_attendances_for_weekday(self, day_dt, calendars):
        """
        Given a day datetime, return matching attendances
        :param day_dt:
        :param calendars:
        :return: recordset: <procurement.calendar.attendance>
        """
        self.ensure_one()
        weekday = day_dt.weekday()
        attendances = self.env['procurement.calendar.attendance']

        domain = self._get_attendances_domain()
        if calendars:
            domain = expression.AND([
                [('procurement_calendar_id', 'in', calendars.ids)],
                domain
            ])
        attendances = attendances.search(domain)

        product_attendances = attendances.filtered(
            lambda a: any(
                product_id == self.product_id.id for product_id in
                a.product_ids.ids))
        filtered_attendances = product_attendances or attendances

        result_attendances = self.env['procurement.calendar.attendance']

        for attendance in filtered_attendances.filtered(
                lambda att: int(att.dayofweek) == weekday and not (
                    att.date_from and
                    fields.Date.from_string(att.date_from) > day_dt.date()
                ) and not (
                    att.date_to and fields.Date.from_string(att.date_to) <
                    day_dt.date()
                )):
            result_attendances |= attendance
        return result_attendances

    def _get_attendances_domain(self):
        """
        We get either attendances without product dependency or
        if true, we check that the product corresponds
        :return: domain
        """
        domain = []
        product_domain = expression.OR([
            [('product_dependant', '=', False)],
            [('product_ids', 'in', self.product_id.ids)]
        ])
        domain = expression.AND([
            product_domain, domain
        ])
        return domain

    @api.multi
    def _get_calendar_supplier_domain(self):
        """
        We get calendar domain depending on suppliers defined on product
        supplierinfo (the right one is computed later)
        :return:
        """
        sellers = self.product_id.seller_ids.mapped('name')
        domain = []
        if sellers:
            domain = [('partner_id', 'in', sellers.ids)]
        product_domain = expression.OR([
            [('product_dependant', '=', False)],
            [('attendance_ids.product_ids', 'in', self.product_id.ids)]
        ])
        domain = expression.AND([
            product_domain, domain
        ])
        return domain
