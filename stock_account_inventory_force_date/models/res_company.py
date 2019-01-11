# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    standard_cost_change_account_id = fields.Many2one(
        'account.account', string='Standard Cost Change Offsetting Account')
    force_inventory_lock_date = fields.Date(
        string="Force Inventory Lock Date",
        help="If set, it won't be possible for any user to force an inventory,"
             "adjustment using a date earlier than this one.")
