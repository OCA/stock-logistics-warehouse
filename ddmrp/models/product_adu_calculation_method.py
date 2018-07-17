# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class ProductAduCalculationMethod(models.Model):
    _name = 'product.adu.calculation.method'
    _description = 'Product Average Daily Usage calculation method'

    @api.model
    def _get_calculation_method(self):
        return [
            ('fixed', _('Fixed ADU')),
            ('past', _('Past-looking')),
            ('future', _('Future-looking'))]

    name = fields.Char(string="Name", required=True)

    method = fields.Selection("_get_calculation_method",
                              string="Calculation method")

    use_estimates = fields.Boolean(sting="Use estimates/forecasted values")
    horizon = fields.Float(string="Horizon",
                           help="Length-of-period horizon in days")

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self:
        self.env['res.company']._company_default_get(
            'product.adu.calculation.method'))

    @api.multi
    @api.constrains('method', 'horizon')
    def _check_horizon(self):
        for rec in self:
            if rec.method in ['past', 'future'] and not rec.horizon:
                raise UserError(_('Please indicate a length-of-period '
                                  'horizon.'))
