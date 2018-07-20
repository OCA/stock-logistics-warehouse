# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockInventoryUninventoriedLocation(models.TransientModel):
    _name = 'stock.inventory.uninventoried.locations'
    _description = 'Confirm the uninventoried Locations.'

    location_ids = fields.Many2many(
        comodel_name='stock.location',
        relation='stock_inventory_uninventoried_location_rel',
        column1='location_id', column2='wizard_id',
        string='Uninventoried location', readonly=True,
        default=lambda x: x._get_default_locations())

    def _get_default_locations(self):
        """Initialize view with the list of uninventoried locations."""
        inventories = self.env['stock.inventory'].browse(
            self._context['active_ids'])
        return inventories.get_missing_locations()

    @api.multi
    def confirm_uninventoried_locations(self):
        """Add the missing inventory lines with qty=0 and confirm inventory"""
        inventories = self.env['stock.inventory'].browse(
            self._context['active_ids'])
        inventories.action_done()
        return {'type': 'ir.actions.act_window_close'}
