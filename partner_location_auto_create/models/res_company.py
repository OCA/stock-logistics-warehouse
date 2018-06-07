# © 2015 Savoir-faire Linux
# © 2018 brain-tec AG (Kumar Aberer <kumar.aberer@braintec-group.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_customer_location = fields.Many2one(
        'stock.location', 'Default Customer Location',
        default=lambda self: self.env.ref('stock.stock_location_customers'))

    default_supplier_location = fields.Many2one(
        'stock.location', 'Default Supplier Location',
        default=lambda self: self.env.ref('stock.stock_location_suppliers'))

    @api.multi
    def get_default_location(self, usage):
        "Return the company's default location related to a usage type"
        self.ensure_one()

        return (
            self.default_customer_location if usage == 'customer' else
            self.default_supplier_location)
