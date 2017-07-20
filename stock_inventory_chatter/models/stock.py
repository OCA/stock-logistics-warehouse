<<<<<<< HEAD
"""Docstring models stock."""
=======
# -*- coding: utf-8 -*-
>>>>>>> e9fbf78... [9.0][ADD] stock_inventory_chatter
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

<<<<<<< HEAD
<<<<<<< HEAD
from odoo import api, fields, models


class StockInventory(models.Model):
    """Docstring class StockInventory."""

    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'mail.thread']
=======
from openerp import api, fields, models
=======
from odoo import api, fields, models
>>>>>>> 0d35c52... [MIG] stock_inventory_chatter: Migration to 10.0


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'mail.thread', 'ir.needaction_mixin']
>>>>>>> e9fbf78... [9.0][ADD] stock_inventory_chatter

    partner_id = fields.Many2one(track_visibility='always')
    state = fields.Selection(track_visibility='onchange')
    location_id = fields.Many2one(track_visibility='always')
<<<<<<< HEAD
    filter = fields.Selection(track_visibility='onchange') 
=======
    filter = fields.Selection(track_visibility='onchange')
>>>>>>> e9fbf78... [9.0][ADD] stock_inventory_chatter

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'cancel':
            return 'stock_inventory_chatter.mt_inventory_canceled'
        elif 'state' in init_values and self.state == 'confirm':
            return 'stock_inventory_chatter.mt_inventory_confirmed'
        elif 'state' in init_values and self.state == 'done':
            return 'stock_inventory_chatter.mt_inventory_done'
        return super(StockInventory, self)._track_subtype(init_values)
