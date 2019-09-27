# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    virtual_reservation_defer_pull = fields.Boolean(
        string="Defer Pull using Virtual Reservation",
        default=False,
        help="Do not create chained moved automatically for delivery. "
        "Transfers must be released manually.",
    )
