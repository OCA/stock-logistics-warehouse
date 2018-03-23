# -*- coding: utf-8 -*-
# © 2014 Acsone SA/NV (http://www.acsone.eu)
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, api, models


class GenerateInventoryWizard(models.TransientModel):
    _inherit = "stock.generate.inventory"

    exhaustive = fields.Boolean(string='Exhaustive', default=True)

    @api.multi
    def generate_inventory(self):
        """Force the value of `exhaustive`"""
        return super(GenerateInventoryWizard, self.with_context(
            force_exhaustive=self.exhaustive)).generate_inventory()
