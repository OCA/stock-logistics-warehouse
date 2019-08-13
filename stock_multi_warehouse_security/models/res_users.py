# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, exceptions, _


class ResUsers(models.Model):
    _inherit = "res.users"

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string="Allowed Warehouses",
        required=True)

    @api.constrains('warehouse_id', 'warehouse_ids')
    def _check_warehouse(self):
        if any(user.company_ids and 
               user.company_id not in user.company_ids for user in self):
            raise exceptions.Warning(
                _('The chosen warehouse is not in the allowed warehouses for \
                   this user'))
