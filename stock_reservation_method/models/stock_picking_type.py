# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    reservation_method = fields.Selection(
        [
            ("at_confirm", "At Confirmation"),
            ("manual", "Manually"),
            ("by_date", "Before scheduled date"),
        ],
        "Reservation Method",
        required=True,
        default="at_confirm",
        help="How products in transfers of " "this operation type should be reserved.",
    )
    reservation_days_before = fields.Integer(
        "Days",
        help="Maximum number of days before "
        "scheduled date that products should be reserved.",
    )
    reservation_days_before_priority = fields.Integer(
        "Days when starred",
        help="Maximum number of days before scheduled "
        "date that priority picking products should be reserved.",
    )
