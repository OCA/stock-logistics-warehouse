# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models

_REPLENISH_METHODS = [
    ('replenish', 'Replenished'),
    ('replenish_override', 'Replenished override'),
    ('min_max', 'Min-max')
]
_ITEM_TYPES = [
    ('manufactured', 'Manufactured'),
    ('purchased', 'Purchased'),
    ('distributed', 'Distributed')
]


class StockBufferProfile(models.Model):
    _name = 'stock.buffer.profile'
    _string = 'Buffer Profile'

    @api.multi
    @api.depends("item_type", "lead_time_id", "lead_time_id.name",
                 "lead_time_id.factor", "variability_id",
                 "variability_id.name", "variability_id.factor")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            rec.name = '%s %s, %s(%s), %s(%s)' % (rec.replenish_method,
                                                  rec.item_type,
                                                  rec.lead_time_id.name,
                                                  rec.lead_time_id.factor,
                                                  rec.variability_id.name,
                                                  rec.variability_id.factor)

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    replenish_method = fields.Selection(string="Replenishment method",
                                        selection=_REPLENISH_METHODS,
                                        required=True)
    item_type = fields.Selection(string="Item Type", selection=_ITEM_TYPES,
                                 required=True)
    lead_time_id = fields.Many2one(
        comodel_name='stock.buffer.profile.lead.time',
        string='Lead Time Factor')
    variability_id = fields.Many2one(
        comodel_name='stock.buffer.profile.variability',
        string='Variability Factor')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.buffer.profile'))
