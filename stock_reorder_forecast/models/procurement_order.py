# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    #disable making PO's from procurement orders


    @api.returns('self', lambda x: x.id)
    def create(self, vals):
        import pudb
        pudb.set_trace()
        if procurement.rule_id and procurement.rule_id.action == 'buy':
            res = super(ProcurementOrder, self.with_context(
                procurement_autorun_defer=True)).create(vals)
            self.unlink(res)
            return False
        return super(ProcurementOrder, self).create(vals)
