# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProcurementOrderpointCompute(models.TransientModel):
    _inherit = 'procurement.orderpoint.compute'

    @api.multi
    def procure_calculation(self):
        """Limit search for processing order point procurement."""
        this = self.with_context(processing_minimum_stock_rules=True)
        super(
            ProcurementOrderpointCompute, this
        ).procure_calculation()
