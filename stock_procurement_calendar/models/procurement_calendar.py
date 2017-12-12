# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcurementCalendar(models.Model):

    _name = 'procurement.calendar'
    _inherits = {'resource.calendar': 'resource_id'}
    _description = 'Procurement Calendar'

    active = fields.Boolean(
        default=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        index=True
    )
    resource_id = fields.Many2one(
        'resource.calendar',
        required=True,
        auto_join=True,
        ondelete='cascade',
        index=True
    )
    attendance_ids = fields.One2many(
        'procurement.calendar.attendance',
        'procurement_calendar_id',
        string="Attendances"
    )
    product_dependant = fields.Boolean()
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        index=True
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )

    _sql_constraints = [
        ('location_uniq',
         'unique (active, location_id)',
         'You cannot have several active calendars for one location.'),
    ]
    _sql_constraints = [
        ('warehouse_uniq',
         'unique (active, warehouse_id)',
         'You cannot have several active calendars for one warehouse.'),
    ]

    @api.multi
    def get_attendances_for_weekday(self, day_dt):
        """
        Helper that calls the resource.calendar function
        :param day_dt:
        :return:
        """
        self.ensure_one()
        attendances = self.resource_id.get_attendances_for_weekday(day_dt)
        p_attendances = self.mapped('attendance_ids').filtered(
            lambda a: a.attendance_id in attendances)
        return p_attendances

    @api.multi
    def unlink(self):
        """
        When we unlink procurement.calendar, we unlink the resource.calendar
        :return:
        """
        self.mapped('resource_id').unlink()
        res = super(ProcurementCalendar, self).unlink()
        return res
