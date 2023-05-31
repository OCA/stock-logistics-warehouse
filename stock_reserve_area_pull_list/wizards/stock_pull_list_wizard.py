# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class PullListWizard(models.TransientModel):
    _inherit = "stock.pull.list.wizard"

    only_reserved_in_area = fields.Boolean()

    def _get_moves_demand_domain(self):
        domain = super()._get_moves_demand_domain()
        if self.only_reserved_in_area:
            domain.append(("area_reserved_availability", "!=", 0))
        return domain
