# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Lockdown",
    "summary": "Prevent to add stock on locked locations",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "version": "15.0.1.0.1",
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
