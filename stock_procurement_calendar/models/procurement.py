# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.osv import expression


class ProcurementOrder(models.Model):

    _name = 'procurement.order'
    _inherit = [
        'procurement.order',
        'procurement.calendar.mixin',
        'mail.thread'
    ]

    _location_field = 'location_id'
    _source_location_field = 'rule_id.location_src_id'

    aimed_attendance_ids = fields.Many2many(
        'procurement.calendar.attendance',
        compute='_compute_aimed_attendance_ids'
    )
    scheduled_next_attendance_id = fields.Many2one(
        'procurement.calendar.attendance',
        compute='_compute_scheduled_next_attendance_id',
        help="The next attendance scheduled for the procurement source. This "
        "is the one that will be used when procurement order will be run"
    )
    scheduled_next_attendance_date = fields.Datetime(
        compute='_compute_scheduled_next_attendance_id',
        help="This is the next scheduled procurement attendance according"
             "to procurement calendars. If this date is different from the"
             "Scheduled Date, the procurement fulfillment could be late."
    )

    @api.multi
    def get_attendances_for_weekday(self, day_dt):
        """ Given a day datetime, return matching attendances """
        self.ensure_one()
        weekday = day_dt.weekday()
        attendances = self.env['procurement.calendar.attendance']

        for attendance in self.aimed_attendance_ids.filtered(
                lambda att: int(att.dayofweek) == weekday and
                not (att.date_from and fields.Date.from_string(
                    att.date_from) > day_dt.date()) and
                not (att.date_to and fields.Date.from_string(
                    att.date_to) < day_dt.date())):
            attendances |= attendance
        return attendances

    @api.multi
    @api.depends('aimed_attendance_ids')
    def _compute_scheduled_next_attendance_id(self, limit=100):
        """
        Compute the next attendance and the next scheduled date
        :param limit:
        :return:
        """
        for procurement in self.filtered(
                lambda p: p.aimed_attendance_ids):
            procurement_date = fields.Datetime.from_string(
                procurement.date_planned) or fields.Datetime.from_string(
                fields.Datetime.now())
            i = 0
            while i <= limit:
                attendances = procurement.get_attendances_for_weekday(
                    procurement_date)
                if attendances:
                    attendance = attendances[0]
                    procurement.scheduled_next_attendance_id = attendance
                    p_date = attendance.get_datetime_start(
                        fields.Date.to_string(procurement_date)
                    )
                    procurement.scheduled_next_attendance_date = p_date
                    break
                procurement_date = procurement_date + relativedelta(days=1)
                i += 1

    @api.multi
    def _compute_aimed_attendance_ids(self):
        """
        Helper field to compute the attendances for the weekday
        :return:
        """
        attendance_obj = self.env['procurement.calendar.attendance']
        for procurement in self.filtered(lambda p: p.procurement_calendar_id):
            attendances = attendance_obj.search(
                procurement._get_source_attendance_domain()
            )
            # Filtered product specific attendances
            product_attendances = attendances.filtered(
                lambda a: any(
                    product_id == procurement.product_id.id for product_id in
                    a.product_ids.ids))
            procurement.aimed_attendance_ids =\
                product_attendances or attendances

    @api.multi
    def _get_source_attendance_domain(self, forward=True):
        """
        Returns the domain to search in procurement.calendar.attendance
        :param forward:
        :return:
        """
        self.ensure_one()
        domain = []
        domain = expression.AND([
            [('procurement_calendar_id',
              '=',
              self.procurement_calendar_id.id)],
            domain
        ])
        # Filter product dependant attendances
        product_domain = expression.OR([
            [('product_dependant', '=', False)],
            [('product_ids', 'in', self.product_id.ids)]
        ])
        domain = expression.AND([
            product_domain, domain
        ])
        return domain

    @api.multi
    def _assign_source_attendance(self):
        """
        We check here the attendance set on procurement and find the right
        one for the source
        :return:
        """
        for procurement in self.filtered(
                lambda p: p.procurement_calendar_id):
            procurement.procurement_attendance_id =\
                procurement.scheduled_next_attendance_id

    def _get_stock_move_values(self):
        res = super(ProcurementOrder, self)._get_stock_move_values()
        # scheduled_date = self._get_procurement_scheduled_date()
        return res

    def _assign(self):
        """
        We catch the rule assignement to update calendar procurement
        :return:
        """
        res = super(ProcurementOrder, self)._assign()
        if res and self.rule_id:
            self._assign_procurement_source_calendar()
            self._assign_source_attendance()
        if self.scheduled_next_attendance_id and\
                self.scheduled_next_attendance_date:
            self.date_planned = self.scheduled_next_attendance_date
            self.message_post(
                _('The scheduled date has been changed to : %s')
                % self._fields['date_planned'].convert_to_display_name(
                    self.date_planned, self))
        self._assign_procurement_destination_calendar()
        self._assign_procurement_destination_attendance()
        return res
