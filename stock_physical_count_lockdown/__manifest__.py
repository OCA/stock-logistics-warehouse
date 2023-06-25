# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Stock Physical Count Lockdown",
    "summary": "Prevent to add stock on locked locations",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": [
        "views/stock_location.xml",
        "security/ir.model.access.csv",
        "wizards/stock_location_lock_view.xml",
    ],
}
