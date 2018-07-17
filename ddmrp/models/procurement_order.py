# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    add_to_net_flow_equation = fields.Boolean(
        string='Pending add net flow equation', default=True,
        readonly=True,
        help="If this flag is set, the procurement is pending to be included "
             "into the net flow equation.")

    @api.multi
    def write(self, vals):
        res = super(ProcurementOrder, self).write(vals)
        if 'state' in vals.keys() \
                and vals['state'] not in ['draft', 'cancel'] \
                and 'add_to_net_flow_equation' not in vals:
            for rec in self:
                if rec.state in ['draft', 'cancel']:
                    rec.add_to_net_flow_equation = True
        return res

    @api.model
    def _procure_orderpoint_confirm(self, use_new_cursor=False,
                                    company_id=False):
        """ Override the standard method to disable the possibility to
        automatically create procurements based on order points.
        With DDMRP it is in the hands of the planner to manually
        create procurements, based on the procure recommendations."""
        return {}
