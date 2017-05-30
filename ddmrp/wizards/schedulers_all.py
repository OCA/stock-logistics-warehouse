# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class ProcurementComputeAll(models.TransientModel):
    _inherit = 'procurement.order.compute.all'

    def procure_calculation(self, cr, uid, ids, context=None):

        raise UserError(_('The option to compute minumum stock rules '
                          'automatically has been disabled.'))
