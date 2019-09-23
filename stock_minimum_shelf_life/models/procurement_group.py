# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_lot_min_expiration_date(self):
        months_adjust = self.env.user.company_id.minimum_shelf_life
        return datetime.now() + relativedelta(hour=0, minute=0, second=0,
                                              months=+months_adjust)
