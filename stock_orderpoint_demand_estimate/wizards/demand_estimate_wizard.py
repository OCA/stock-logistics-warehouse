# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError

_PERIOD_SELECTION = [
    ('monthly', 'Monthly'),
    ('weekly', 'Weekly')
]


class DemandEstimateSheet(models.TransientModel):
    _name = 'demand.estimate.sheet'
    _description = 'Stock Orderpoint Demand Estimate'

    def _default_date_from(self):
        return self.env.context.get('date_from', False)

    def _default_date_to(self):
        return self.env.context.get('date_to', False)

    def _default_location_id(self):
        location_id = self.env.context.get('location_id', False)
        if location_id:
            return self.env['stock.location'].browse(location_id)
        else:
            return False

    def _default_period_type(self):
        return self.env.context.get('period_type', False)

    def _default_estimate_ids(self):
        period_type = self.env.context.get('period_type', False)
        date_from = self.env.context.get('date_from', False)
        date_to = self.env.context.get('date_to', False)
        orderpoint_ids = self.env.context.get('orderpoint_ids', False)
        domain = [('period_type', '=', period_type),
                  ('date_from', '>=', date_from),
                  ('date_to', '<=', date_to)]
        periods = self.env['stock.orderpoint.demand.estimate.period'].search(
            domain)
        orderpoints = self.env['stock.warehouse.orderpoint'].browse(orderpoint_ids)

        lines = []
        for orderpoint in orderpoints:
            name_y = ''
            if orderpoint.product_id.default_code:
                name_y += '[%s] ' % orderpoint.product_id.default_code
            name_y += orderpoint.product_id.name
            name_y += ' - %s' % orderpoint.product_id.uom_id.name
            for period in periods:
                estimates = self.env['stock.orderpoint.demand.estimate'].search(
                    [('orderpoint_id', '=', orderpoint.id),
                     ('period_id', '=', period.id)])
                if estimates:
                    lines.append((0, 0, {
                        'value_x': period.name,
                        'value_y': name_y,
                        'period_id': period.id,
                        'orderpoint_id': orderpoint.id,
                        'estimate_id': estimates[0].id,
                        'product_uom_qty': estimates[0].product_uom_qty
                    }))
                else:
                    lines.append((0, 0, {
                        'value_x': period.name,
                        'value_y': name_y,
                        'period_id': period.id,
                        'orderpoint_id': orderpoint.id,
                        'product_uom_qty': 0.0
                    }))
        return lines

    date_from = fields.Date(string="Date From", readonly=True,
                            default=_default_date_from)
    date_to = fields.Date(string="Date From", readonly=True,
                          default=_default_date_to)
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location", readonly=True,
                                  default=_default_location_id)
    period_type = fields.Selection(string="Period Type",
                                   selection=_PERIOD_SELECTION,
                                   default=_default_period_type,
                                   readonly=True)

    line_ids = fields.Many2many(
        string="Estimates",
        comodel_name='demand.estimate.sheet.line',
        rel='demand_estimate_line_rel',
        default=_default_estimate_ids)

    @api.model
    def _prepare_estimate_data(self, line):
        return {
            'period_id': line.period_id.id,
            'orderpoint_id': line.orderpoint_id.id,
            'product_uom_qty': line.product_uom_qty
        }

    @api.multi
    def button_validate(self):
        res = []
        for line in self.line_ids:
            if line.estimate_id:
                line.estimate_id.product_uom_qty = line.product_uom_qty
                res.append(line.estimate_id.id)
            else:
                data = self._prepare_estimate_data(line)
                estimate = self.env['stock.orderpoint.demand.estimate'].create(
                    data)
                res.append(estimate.id)
        res = {
            'domain': [('id', 'in', res)],
            'name': _('Stock orderpoint Demand Estimates'),
            'src_model': 'stock.orderpoint.demand.estimate.wizard',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.orderpoint.demand.estimate',
            'type': 'ir.actions.act_window'
        }
        return res


class DemandEstimateSheetLine(models.TransientModel):
    _name = 'demand.estimate.sheet.line'
    _description = 'Demand Estimate Sheet Line'

    estimate_id = fields.Many2one(comodel_name='stock.orderpoint.demand.estimate')
    period_id = fields.Many2one(
        comodel_name='stock.orderpoint.demand.estimate.period')
    orderpoint_id = fields.Many2one(comodel_name='stock.warehouse.orderpoint')
    value_x = fields.Char(string='Period')
    value_y = fields.Char(string='orderpoint')
    product_uom_qty = fields.Float(
        string="Quantity", digits_compute=dp.get_precision('Product UoM'))


class DemandEstimateWizard(models.TransientModel):
    _name = 'demand.estimate.wizard'
    _description = 'Stock orderpoint Demand Estimate Wizard'

    def _default_period_type(self):
        return 'monthly'

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    period_type = fields.Selection(string="Period Type",
                                   selection=_PERIOD_SELECTION,
                                   required=True,
                                   default=_default_period_type)
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location", required=True)
    orderpoint_ids = fields.Many2many(comodel_name="stock.warehouse.orderpoint",
                                  relation='demand_estimate_wiz_orderpoint_rel',
                                  string="Stock orderpoints",
                                  domain="[('location_id', '=', location_id)]")

    @api.multi
    def _prepare_demand_estimate_sheet(self):
        self.ensure_one()
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'period_type': self.period_type,
            'location_id': self.location_id.id,
        }

    @api.multi
    def create_sheet(self):
        self.ensure_one()
        if not self.orderpoint_ids:
            raise UserError(_('You must select at lease one Stock orderpoint.'))

        context = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'period_type': self.period_type,
            'location_id': self.location_id.id,
            'orderpoint_ids': self.orderpoint_ids.ids
        }
        res = {
            'context': context,
            'name': _('Estimate Sheet'),
            'src_model': 'demand.estimate.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'demand.estimate.sheet',
            'type': 'ir.actions.act_window'
        }

        return res
