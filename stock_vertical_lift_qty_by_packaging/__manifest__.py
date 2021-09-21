# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Stock vertical lift qty by packaging",
    "summary": """
    Glue module for `stock_product_qty_by_packaging` and `stock_vertical_lift`.
    """,
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["stock_product_qty_by_packaging", "stock_vertical_lift"],
    "data": ["views/vertical_lift_operation_base_views.xml"],
}
