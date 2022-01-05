# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def _get_moves_to_assign_domain(self, company_id):
        domain = super(ProcurementGroup, self)._get_moves_to_assign_domain(company_id)
        domain = expression.AND(
            [domain, [("reservation_date", "<=", fields.Date.today())]]
        )
        return domain
