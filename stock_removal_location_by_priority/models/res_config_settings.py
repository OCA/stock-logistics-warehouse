# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_removal_priority = fields.Boolean(
        string="Removal Priority",
        implied_group='stock_removal_location_by_priority.'
                      'group_removal_priority',
        help="Removal priority that applies when the incoming dates "
             "are equal in both locations.",
    )
