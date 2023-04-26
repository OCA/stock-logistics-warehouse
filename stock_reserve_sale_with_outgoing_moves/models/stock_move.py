# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    used_for_sale_reservation = fields.Boolean(default=False)

    def _action_assign(self):
        self = self.filtered(lambda m: not m.used_for_sale_reservation)
        return super(StockMove, self)._action_assign()
