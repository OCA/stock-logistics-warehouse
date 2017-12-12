# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time
import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.resource.models.resource import hours_time_string


class ProcurementCalendarAttendance(models.Model):

    _name = 'procurement.calendar.attendance'
    _inherits = {'resource.calendar.attendance': 'attendance_id'}
    _description = 'Procurement Calendar Attendance'

    attendance_id = fields.Many2one(
        'resource.calendar.attendance',
        string='Attendance',
        auto_join=True,
        required=True,
        ondelete='cascade',
    )
    procurement_calendar_id = fields.Many2one(
        'procurement.calendar',
        string='Calendar',
        required=True,
        readonly=True,
    )
    product_dependant = fields.Boolean(
        related='procurement_calendar_id.product_dependant',
        readonly=True
    )
    product_ids = fields.Many2many(
        'product.product',
        'calendar_attendance_product_product_rel',
        'attendance_id',
        'product_id',
        string='Products',
    )
    procurement_attendance_id = fields.Many2one(
        'procurement.calendar.attendance',
        string="Scheduled Procurement",
        help="This is the expected delivery slot."
    )

    @api.model
    def create(self, vals):
        if 'procurement_calendar_id' in vals and 'calendar_id' not in vals:
            calendar = self.env['procurement.calendar'].browse(
                vals['procurement_calendar_id'])
            vals.update({'calendar_id': calendar.resource_id.id})
        return super(ProcurementCalendarAttendance, self).create(vals)

    @api.multi
    def unlink(self):
        self.mapped('attendance_id').unlink()
        res = super(ProcurementCalendarAttendance, self).unlink()
        return res

    @api.multi
    def get_datetime_start(self, att_date=fields.Date.today()):
        """
        Helps to get a datetime depending on attendance hours and weekday
        As hours are not timezone dependant, we convert to utc
        :param att_date: fields.Date
        :return:
        """
        self.ensure_one()
        # We get the attendance date() and weekday
        att_date = fields.Date.from_string(att_date)
        weekday = att_date.weekday()

        # We change the attendance date to match the range
        if self.date_from and att_date < self.date_from:
            att_date = self.date_from
        elif self.date_to and att_date > self.date_to:
            att_date = self.date_to
        if int(self.dayofweek) != weekday:
            att_date = att_date + relativedelta(weekday=int(self.dayofweek))

        att_date = fields.Datetime.from_string(
            fields.Datetime.to_string(att_date))
        if self.hour_from:
            hours_time = hours_time_string(self.hour_from).split(':')
            att_time = time(
                hour=int(hours_time[0]), minute=int(hours_time[1]))
            att_datetime = self.convert_date_time_to_utc(att_date, att_time)
        elif self.hour_to:
            hours_time = hours_time_string(self.hour_to).split(':')
            att_time = time(
                hour=int(hours_time[0]), minute=int(hours_time[1]))
            att_datetime = self.convert_date_time_to_utc(att_date, att_time)
        else:
            att_datetime = att_date
        return att_datetime

    def convert_date_time_to_utc(self, att_date, att_time):
        """
        We convert a date and a time to utc depending on context timezone
        :param att_date: date()
        :param att_time: time()
        :return: datetime()
        """
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        utc = pytz.utc
        att_datetime = datetime.combine(att_date, att_time)
        att_datetime = tz.localize(att_datetime)
        att_datetime = att_datetime.astimezone(utc)
        return att_datetime
