# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    #disable making PO's from procurement orders


    @api.model
    def create(self, vals):
        if vals['origin'][:2] == 'SO':
            res = super(ProcurementOrder, self.with_context(
                procurement_autorun_defer=True, 
                tracking_disable=False,
                mail_create_nosubscribe=True,
                mail_create_nolog=True,
                mail_notrack=True, 
                )).create(vals)
            res.write({'state':'cancel'})
            super(ProcurementOrder, res).unlink()
            return self
        return super(ProcurementOrder, self).create(vals)
