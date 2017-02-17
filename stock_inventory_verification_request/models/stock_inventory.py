# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    requested_verification = fields.Boolean(string='Requested Verification?',
                                            default=False, copy=False)
    slot_verification_ids = fields.One2many(
        comodel_name='stock.slot.verification.request',
        string='Slot Verification Requests', inverse_name='inventory_id')

    @api.multi
    def action_request_verification(self):
        self.requested_verification = True
        for line in self.line_ids:
            if line.discrepancy_threshold and (line.discrepancy_percent >
                                               line.discrepancy_threshold):
                self.env['stock.slot.verification.request'].create({
                    'inventory_id': self.id,
                    'inventory_line_id': line.id,
                    'location_id': line.location_id.id,
                    'state': 'wait',
                    'product_id': line.product_id.id,
                })


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    # TODO: make this work
    slot_verification_ids = fields.One2many(
        comodel_name='stock.slot.verification.request',
        inverse_name='inventory_line_id',
        string='Slot Verification Request')

    @api.multi
    def action_open_svr(self):
        '''
        Open the corresponding Slot Verification Request directly from the
        Inventory Lines.
        '''
        request_svr_ids = []
        for line in self:
            request_svr_ids += line.slot_verification_ids.ids
        domain = [('id', 'in', request_svr_ids)]
        return {'name': _('Slot Verification Request'),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.slot.verification.request',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}
