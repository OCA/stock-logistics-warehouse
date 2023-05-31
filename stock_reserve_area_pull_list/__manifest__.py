# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Reserve Area Pull List",
    "summary": "Adds Only Reserved in Area filtering",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "maintainers": ["mariadforgeflow"],
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "depends": ["stock_pull_list", "stock_reserve_area"],
    "data": [
        "wizards/stock_pull_list_wizard.xml",
    ],
    "installable": True,
}
