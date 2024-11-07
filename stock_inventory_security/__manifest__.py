# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Inventory Security",
    "summary": "Dedicated security group to apply inventory adjustments",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": ["stock"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/stock_quant.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
}
