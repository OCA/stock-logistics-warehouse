# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Request BOM",
    "summary": "Stock Request with BOM Integration",
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock_request", "mrp"],
    "data": [
        "views/stock_request_order_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
