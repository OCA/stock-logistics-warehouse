# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _is_child(self, location):
        self.ensure_one()
        if self == location:
            return True
        elif self.location_id:
            return self.location_id._is_child(location)
        else:
            return False
