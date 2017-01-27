# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    requested_verification = fields.Boolean(string='Requested Verification?',
                                            default=False)

    @api.model
    def action_over_discrepancies(self):
        raise UserError(
            _('Cannot validate the Inventory Adjustment.\n Found %s over '
              'discrepancies.  You may consider requesting a verification') %
            self.over_discrepancies)

    @api.multi
    def action_request_verification(self):
        self.requested_verification = True
        self.env['stock.slot.verification.request'].create({
            'inventory_id': self.id,
            'status': 'wait',
        })
