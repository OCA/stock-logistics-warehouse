##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_customer_location = fields.Many2one(
        "stock.location",
        "Default Customer Location",
        default=lambda self: self.env.ref("stock.stock_location_customers"),
    )

    default_supplier_location = fields.Many2one(
        "stock.location",
        "Default Supplier Location",
        default=lambda self: self.env.ref("stock.stock_location_suppliers"),
    )

    @api.multi
    def get_default_location(self, usage):
        "Return the company's default location related to a usage type"
        self.ensure_one()

        return (
            self.default_customer_location
            if usage == "customer"
            else self.default_supplier_location
        )
