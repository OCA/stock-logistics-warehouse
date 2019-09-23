# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    minimum_shelf_life = fields.Integer(
        default=6,
        string="Minimum shelf life (in months)"
    )
