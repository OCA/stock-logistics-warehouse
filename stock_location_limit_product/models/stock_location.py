# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    limit_ids = fields.One2many('stock.location.limit',
                                'location_id',
                                'Limits')
