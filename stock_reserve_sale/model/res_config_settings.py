# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_stock_reservation_policy = fields.Selection(
        related="company_id.sale_stock_reservation_policy",
        readonly=False,
    )
    sale_stock_reservation_picking = fields.Boolean(
        related="company_id.sale_stock_reservation_picking",
        readonly=False,
    )
