# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Stock Exception",
    "summary": "Custom exceptions on stock picking",
    "version": "16.0.1.1.0",
    "category": "Generic Modules/Warehouse Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock", "base_exception"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/stock_exception_data.xml",
        "wizard/stock_exception_confirm_view.xml",
        "views/stock_view.xml",
    ],
    "installable": True,
}
