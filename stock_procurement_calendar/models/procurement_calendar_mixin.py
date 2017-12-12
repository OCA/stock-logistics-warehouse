# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProcurementCalendarMixin(models.AbstractModel):

    _name = 'procurement.calendar.mixin'

    # Helper fields
    _location_field = False
    _location_source_field = False
    _warehouse_field = False
    _partner_field = False

    procurement_calendar_id = fields.Many2one(
        'procurement.calendar',
        index=True,
        help="The source Procurement Calendar"
    )
    procurement_attendance_id = fields.Many2one(
        'procurement.calendar.attendance',
        index=True,
        help="The source Procurement Calendar Attendance"
    )
    procurement_destination_calendar_id = fields.Many2one(
        'procurement.calendar',
        index=True,
        help="The destination Procurement Calendar"
    )
    procurement_destination_attendance_id = fields.Many2one(
        'procurement.calendar.attendance',
        index=True,
        help="The destination Procurement Calendar Attendance"
    )

    @api.multi
    def _get_calendar_location_domain(self, location=False):
        self.ensure_one()
        if not location:
            location = self.mapped(self._location_field)
        domain = [('location_id', 'in', location.ids)]
        return domain

    @api.multi
    def _get_calendar_location_warehouse_domain(self, location=False):
        self.ensure_one()
        if not location:
            location = self.mapped(self._location_field)
        domain = [(
            'warehouse_id.view_location_id',
            'parent_of',
            location.id
        )]
        return domain

    @api.multi
    def _assign_procurement_destination_calendar(self):
        """
        We search for calendar defined for the procurement location
        :return:
        """
        calendar_obj = self.env['procurement.calendar']
        for mixin in self:
            # 0 A destination attendance is associated with the procurement
            # attendance : we force the selection
            if mixin.procurement_attendance_id and\
                    mixin.procurement_attendance_id.procurement_attendance_id:
                dest_attendance =\
                    mixin.procurement_attendance_id.procurement_attendance_id
                mixin.procurement_destination_calendar_id =\
                    dest_attendance.procurement_calendar_id
                mixin.procurement_destination_attendance_id = dest_attendance
                continue
            # 1 Search for calendars with location defined
            calendar = calendar_obj.search(
                mixin._get_calendar_location_domain(),
                limit=1
            )
            if not calendar:
                # 2 Search for calendars with warehouse defined
                calendar = calendar_obj.search(
                    mixin._get_calendar_location_warehouse_domain(),
                    limit=1
                )
            mixin.procurement_destination_calendar_id = calendar

    @api.multi
    def _assign_procurement_destination_attendance(self):
        for mixin in self.filtered(
                lambda p: p.procurement_destination_calendar_id and not
                p.procurement_destination_attendance_id):
            date_t = datetime.strptime(
                fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
            cal = mixin.procurement_destination_calendar_id
            attendances = cal.get_attendances_for_weekday(date_t)
            if attendances:
                mixin.procurement_destination_attendance_id = attendances[0]

    @api.multi
    def _assign_procurement_source_calendar(self):
        """
        We search for calendar defined for the procurement source
        :return:
        """
        calendar_obj = self.env['procurement.calendar']
        not_assigned_mixins = self.filtered(
            lambda p: not p.procurement_calendar_id)
        for mixin in not_assigned_mixins:
            # 1 Search for calendars with location defined
            source_location = mixin.mapped(self._location_source_field)
            if source_location:
                calendar = calendar_obj.search(
                    mixin._get_calendar_location_domain(
                        location=mixin.rule_id.location_src_id),
                    limit=1
                )
                # 2 Search for calendars with warehouse defined
                if not calendar and mixin.rule_id.location_src_id:
                    calendar = calendar_obj.search(
                        mixin._get_calendar_location_warehouse_domain(
                            location=mixin.rule_id.location_src_id
                        ),
                        limit=1
                    )
                if calendar:
                    mixin.procurement_calendar_id = calendar
