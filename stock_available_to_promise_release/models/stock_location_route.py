# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Route(models.Model):
    _inherit = "stock.location.route"

    available_to_promise_defer_pull = fields.Boolean(
        string="Release based on Available to Promise",
        default=False,
        help="Do not create chained moved automatically for delivery. "
        "Transfers must be released manually when they have enough available"
        " to promise.",
    )
