# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    product_id = fields.Many2one("product.product", index=True)
