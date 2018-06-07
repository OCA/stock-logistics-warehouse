# © 2018 brain-tec AG (Kumar Aberer <kumar.aberer@braintec-group.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_customer_location = fields.Many2one(
        related='company_id.default_customer_location')
    default_supplier_location = fields.Many2one(
        related='company_id.default_supplier_location')
