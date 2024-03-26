# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    """Defines Minimum stock rules."""

    _inherit = "stock.warehouse.orderpoint"

    template_id = fields.Many2one(
        "stock.warehouse.orderpoint.template",
        "Template",
        check_company=True,
        ondelete="cascade",
    )
