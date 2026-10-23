# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

SALE_STOCK_RESERVATION_POLICIES = [
    ("always", "Always reserve the ordered quantity"),
    ("partial", "Reserve the available quantity"),
    ("full", "Reserve only if the full quantity is available"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_stock_reservation_policy = fields.Selection(
        SALE_STOCK_RESERVATION_POLICIES,
        string="Stock Reservation Policy",
        required=True,
        default="always",
    )
