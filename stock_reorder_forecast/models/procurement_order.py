# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    #disable making PO's from procurement orders

    @api.model
    def _run(self, procurement):
        if (procurement.rule_id and procurement.rule_id.action == 'buy'):
            return True
        return super(ProcurementOrder, self)._run(procurement)
