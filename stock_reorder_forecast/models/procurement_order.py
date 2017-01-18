# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    #disable making PO's from procurement orders
    
    # this would defer the creation of PO but it would be triggered anyway on
    # scheduler.
    """
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
            return self
        return super(ProcurementOrder, self).create(vals)
    """

    @api.multi
    def run(self):
        for procurement in self:
            if ((procurement.rule_id and procurement.rule_id.action == 'buy') 
                    or procurement.origin[:2] == 'SO'):
                # Skip po will trigger in make_po to skip PO creation for buy
                # products and return the procurement.id as if they where
                # processed, without hchanging the state though, because our
                # query also relies on procurements to create orders.
                return self.with_context(skip_po=True)._run(procurement)
        return super(ProcurementOrder, self).run()
   
    # don't create PO's if in skip mode

    @api.multi
    def make_po(self):
        for procurement in self:
            if self.context['skip_po'] == True:
                return procurement.id
            else:
                return super(ProcurementOrder, self).make_po()
