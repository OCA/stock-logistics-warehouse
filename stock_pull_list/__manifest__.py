# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Pull List",
    "summary": "The pull list checks the stock situation and calculates "
               "needed quantities.",
    "version": "12.0.1.0.1",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, "
              "Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "depends": [
        "stock",
        "stock_available_unreserved",
    ],
    "data": [
        "wizards/stock_pull_list_wizard.xml",
    ],
    "installable": True,
}
