# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.multi
    def run(self, autocommit=False):
        # preload data for def check
        self.mapped('orderpoint_id.procurement_calendar_id')
        return super(ProcurementOrder, self).run(autocommit)

    def _procurement_from_orderpoint_get_groups(self, orderpoint_ids):
        orderpoint = self.env['stock.warehouse.orderpoint'].browse(
            orderpoint_ids[0])
        res_groups = []
        date_groups = orderpoint._get_group()
        for date, group in date_groups:
            if orderpoint.procurement_calendar_id and\
                    orderpoint.scheduled_attendance_date:
                res_groups += [{
                    'to_date': fields.Datetime.from_string(
                        orderpoint.scheduled_attendance_date),
                    'procurement_values': {
                        'group': group,
                        'date': fields.Datetime.from_string(
                            orderpoint.scheduled_attendance_date),
                    }
                }]
            else:
                res_groups += [{
                    'to_date': False,
                    'procurement_values': {
                        'group': group,
                        'date': date,
                    }
                }]
        return res_groups

    @api.multi
    def _assign_source_attendance(self):
        """
        We check here the attendance set on procurement and find the right
        one for the source depending on orderpoints
        :return:
        """
        procurements_with_attendance = self.filtered(
            lambda p: p.orderpoint_id.procurement_attendance_id)
        for procurement in procurements_with_attendance:
            procurement.procurement_attendance_id = \
                procurement.orderpoint_id.procurement_attendance_id
        return super(
            ProcurementOrder,
            self - procurements_with_attendance)._assign_source_attendance()

    def _assign_procurement_source_calendar(self):
        assigned_procurements = self.env['procurement.order']
        for procurement in self.filtered(lambda p: p.orderpoint_id):
            calendar = procurement.orderpoint_id.procurement_calendar_id
            if calendar:
                procurement.procurement_calendar_id = calendar
                assigned_procurements += procurement
        return super(
            ProcurementOrder,
            self - assigned_procurements)._assign_procurement_source_calendar()

    @api.multi
    def _prepare_purchase_order(self, partner):
        """
        We define the order date depending on scheduled date
        :param partner:
        :return:
        """
        res = super(
            ProcurementOrder,
            self)._prepare_purchase_order(partner=partner)
        if self.procurement_attendance_id:
            date_order = self.scheduled_next_attendance_date or\
                self.orderpoint_id.scheduled_attendance_date
            res.update({
                'date_order': date_order,
                'procurement_attendance_id': self.procurement_attendance_id.id,
            })
        return res

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        """
        Set purchase order date planned according to destination attendance
        :param po:
        :param supplier:
        :return:
        """
        res = super(
            ProcurementOrder, self)._prepare_purchase_order_line(po, supplier)
        attendance = self.procurement_destination_attendance_id
        if attendance:
            if self.orderpoint_id.scheduled_delivery_date:
                scheduled_date = self.orderpoint_id.scheduled_delivery_date
            else:
                scheduled_date = attendance.get_datetime_start(
                    fields.Date.to_string(
                        fields.Date.from_string(po.date_order)))
            res.update({'date_planned': scheduled_date})
        return res

    @api.multi
    def _make_po_get_domain(self, partner):
        """
        We group here purchases that have the same attendance
        :param partner:
        :return:
        """
        domain = super(ProcurementOrder, self)._make_po_get_domain(
            partner=partner)
        if self.procurement_attendance_id:
            domain += (('procurement_attendance_id',
                        '=',
                        self.procurement_attendance_id.id
                        )),
        else:
            domain += (('procurement_attendance_id',
                        '=',
                        False
                        )),
        return domain

    def _make_po_select_supplier(self, suppliers):
        """
        We select the supplier defined on calendar (if set) because
        it was selected depending on supplierinfo rules
        :param suppliers:
        :return:
        """
        suppliers_in_calendars = suppliers.filtered(
            lambda s: s.name == self.procurement_calendar_id.partner_id)
        if suppliers_in_calendars:
            return suppliers_in_calendars[0]
        else:
            return super(ProcurementOrder, self)._make_po_select_supplier(
                suppliers)

    @api.model
    def _procurement_from_orderpoint_get_grouping_key(self, orderpoint_ids):
        """
        We are grouping here procurements by attendance
        :param orderpoint_ids:
        :return: tuple(
            <stock.warehouse.location>,
            <procurement.calendar.attendance>
            )
        """
        orderpoint = self.env['stock.warehouse.orderpoint'].browse(
            orderpoint_ids[0])
        return (
            orderpoint.location_id.id,
            orderpoint.procurement_attendance_id.id
        )
