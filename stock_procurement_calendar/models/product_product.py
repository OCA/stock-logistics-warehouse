# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):

    _inherit = 'product.product'

    procurement_calendar_count = fields.Integer(
        compute='_compute_procurement_calendar_count'
    )
    procurement_attendance_ids = fields.Many2many(
        'procurement.calendar.attendance',
        compute='_compute_procurement_attendance_ids'
    )

    @api.multi
    def _compute_procurement_attendance_ids(self):
        attendance_obj = self.env['procurement.calendar.attendance']
        for product in self:
            attendances = attendance_obj.search(
                product._get_procurement_calendar_domain()
            )
            product.procurement_attendance_ids = attendances

    @api.multi
    def _get_procurement_calendar_domain(self):
        domain = expression.AND([
            [('product_ids', 'in', self.ids)],
            [('procurement_calendar_id.product_dependant', '=', True)]
        ])
        domain = expression.OR([
            [('procurement_calendar_id.product_dependant', '=', False)],
            domain
        ])
        seller_ids = self.mapped('product_variant_ids.seller_ids.name')
        if seller_ids:
            domain = expression.AND([
                [('procurement_calendar_id.partner_id', 'in', seller_ids.ids)],
                domain
            ])
        return domain

    @api.multi
    def _compute_procurement_calendar_count(self):
        attendances = self.env['procurement.calendar.attendance'].search(
            self._get_procurement_calendar_domain(),
        )
        for product in self:
            product.procurement_calendar_count = len(attendances.filtered(
                lambda a, p=product: p.ids in a.product_ids.ids or
                a.procurement_calendar_id.partner_id.id in
                p.seller_ids.mapped('name.id'))
            )

    @api.multi
    def action_view_procurement_calendars(self):
        self.ensure_one()
        ref = 'stock_procurement_calendar.'\
            'procurement_calendar_attendance_act_window'
        action_dict = self.env.ref(ref).read()[0]
        if action_dict:
            action_dict.update(
                {
                    'domain':
                        [('id', 'in', self.procurement_attendance_ids.ids)]
                }
            )
        return action_dict
