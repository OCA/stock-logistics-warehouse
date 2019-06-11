# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class VerticalLiftShuttle(models.Model):
    _inherit = 'vertical.lift.shuttle'

    @api.model
    def _selection_hardware(self):
        values = super()._selection_hardware()
        values += [('kardex', 'Kardex')]
        return values
