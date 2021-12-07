# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, models
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_moves_to_assign_domain(self, company_id):
        domain = super()._get_moves_to_assign_domain(company_id)
        # Only reserve stock for Transfers with priority set
        return expression.AND([[("priority", "!=", "0")], domain])
