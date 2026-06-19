# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv import expression


class RouteProfile(models.Model):
    _inherit = "route.profile"

    def _domain_route_ids(self):
        domain = super()._domain_route_ids()
        domain = expression.AND([domain, [("internal_supply", "=", False)]])
        return domain
