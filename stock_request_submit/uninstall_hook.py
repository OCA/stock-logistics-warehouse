# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sr = env['stock.request'].search([('state', '=', 'submitted')])
    sr.write({'state': 'draft'})
    sro = env['stock.request.order'].search([('state', '=', 'submitted')])
    sro.write({'state': 'draft'})
