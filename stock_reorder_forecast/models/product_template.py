# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    turnover_average_aggregated = fields.Float(
        'Turnover average', compute='_compute_turnover_average_aggregated',
        readonly=True, store=True,
        help='Average turnover of product variants per day. '
        'Used by the purchase proposal.')

    @api.multi
    @api.depends('product_variant_ids.turnover_average')
    def _compute_turnover_average_aggregated(self):
        for this in self:
            this.turnover_average_aggregated = sum(
                this.mapped('product_variant_ids.turnover_average')
            )
