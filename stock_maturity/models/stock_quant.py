# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models
from odoo.osv import expression


class StockQuant(models.Model):
    _inherit = "stock.quant"

    maturity_date = fields.Datetime(related="lot_id.maturity_date", store=True)

    def _get_gather_domain(self, *args, **kwargs):
        # Don't allow to reserve until the product is mature
        domain = super()._get_gather_domain(*args, **kwargs)
        if self.env.context.get("with_maturity"):
            domain = expression.AND(
                [
                    [
                        "|",
                        ("maturity_date", "<=", self.env.context["with_maturity"]),
                        ("maturity_date", "=", False),
                    ],
                    domain,
                ]
            )
        return domain
