# Copyright 2020-24 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Pull List",
    "summary": "The pull list checks the stock situation and calculates "
    "needed quantities.",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "development_status": "Beta",
    "category": "Warehouse Management",
    "depends": ["stock", "stock_free_quantity"],
    "data": [
        "security/ir.access.csv",
        "wizards/stock_pull_list_wizard.xml",
        "data/stock_pull_list_sequence_data.xml",
        "data/data.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
