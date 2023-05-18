# Copyright 2022 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


# TODO: move to its own file
class WorkCenter(models.Model):
    _inherit = "mrp.workcenter"

    def _get_rollup_cost(self):
        return self.costs_hour
