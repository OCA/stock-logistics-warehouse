# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_lock_cost = fields.Boolean(
        compute="_compute_allow_lock_cost", string="Allow Lock Cost Price"
    )

    def _compute_allow_lock_cost(self):
        for product in self:
            product.allow_lock_cost = (
                True if self.env.user.company_id.lock_cost_products else False
            )
