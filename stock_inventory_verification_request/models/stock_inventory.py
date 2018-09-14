# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    requested_verification = fields.Boolean(
        string='Requested Verification?', copy=False)
    slot_verification_ids = fields.One2many(
        comodel_name='stock.slot.verification.request',
        string='Slot Verification Requests', inverse_name='inventory_id')

    @api.multi
    def action_request_verification(self):
        self.ensure_one()
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
    _rec_name = 'product_id'

    slot_verification_ids = fields.One2many(
        comodel_name='stock.slot.verification.request',
        inverse_name='inventory_line_id',
        string='Slot Verification Request')

    @api.multi
    def action_open_svr(self):
        """Open the corresponding Slot Verification Request directly from the
        Inventory Lines."""
        request_svr_ids = self.mapped('slot_verification_ids').ids
        action = self.env.ref('stock_inventory_verification_request.'
                              'action_slot_verification_request')
        result = action.read()[0]
        if len(request_svr_ids) > 1:
            result['domain'] = [('id', 'in', request_svr_ids)]
        elif len(request_svr_ids) == 1:
            view = self.env.ref(
                'stock_inventory_verification_request.stock_'
                'slot_verification_request_form_view', False)
            result['views'] = [(view and view.id or False, 'form')]
            result['res_id'] = request_svr_ids[0] or False
        return result
