# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockBufferProfileLeadTime(models.Model):
    _name = 'stock.buffer.profile.lead.time'
    _string = 'Buffer Profile Lead Time Factor'

    name = fields.Char(string='Name', required=True)
    factor = fields.Float(string='Variability Factor', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.buffer.profile.lead.time'))
