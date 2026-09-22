# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Vertical Lift Module management - Batch Picking",
    "summary": """
        This module implements the Vertical Warehouses
        functionality at the batch picking level.
        """,
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["adasatorres-tecnativa"],
    "depends": ["stock_vlm_mgmt", "stock_picking_batch"],
    "data": ["views/stock_picking_batch_views.xml"],
}
