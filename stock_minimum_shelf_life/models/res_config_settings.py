# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimum_shelf_life = fields.Integer(
        related='company_id.minimum_shelf_life',
        string="Minimum shelf life (in months)",
        readonly=False
    )
