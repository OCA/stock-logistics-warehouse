# Copyright 2024-2025 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock resupply order",
    "summary": """
        A module that takes the existing stock in the destination
        location into account when creating procurements.
        """,
    "category": "",
    "version": "14.0.1.0.0",
    "author": "Foodles, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": [
        # Odoo
        "base",
        "product",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_resupply_order.xml",
    ],
    "demo": [
        "demo/stock_route_stock_resupply_order.xml",
    ],
    "application": True,
}
