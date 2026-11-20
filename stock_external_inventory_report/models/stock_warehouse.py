# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    external_inventory_user_id = fields.Many2one(
        "res.users",
        string="External Inventory Responsible",
        check_company=True,
        help="Responsible for the discrepancies of the external inventory reports "
        "of the warehouse: their activities are assigned to this user.",
    )
