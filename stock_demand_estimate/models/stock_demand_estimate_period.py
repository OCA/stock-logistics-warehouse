# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class StockDemandEstimatePeriod(models.Model):
    _name = 'stock.demand.estimate.period'
    _description = 'Stock Demand Estimate Period'
    _order = 'date_from'

    @api.multi
    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                rec.days = (fields.Date.from_string(rec.date_to) -
                            fields.Date.from_string(rec.date_from)).days + 1

    name = fields.Char(string="Name", required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    days = fields.Float(string="Days between dates",
                        compute='_compute_days', store=True, readonly=True)

    estimate_ids = fields.One2many(
        comodel_name="stock.demand.estimate",
        inverse_name="period_id")

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.demand.estimate.period'))

    @api.multi
    @api.constrains('name', 'date_from', 'date_to')
    def _check_period(self):
        for period in self:
            self.env.cr.execute('SELECT id, date_from, date_to \
                FROM stock_demand_estimate_period \
                WHERE (date_from <= %s and %s <= date_to) \
                AND id <> %s', (period.date_to, period.date_from, period.id))
            res = self.env.cr.fetchall()
            if res:
                raise UserError(_('Two periods cannot overlap.'))
