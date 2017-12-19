# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Revaluation",
    "summary": "Introduces inventory revaluation as single point to change "
               "the valuation of products.",
    "version": "8.0.1.1.0",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Warehouse",
    "depends": ["stock_account", "product"],
    "license": "AGPL-3",
    "data": [
        "wizards/stock_inventory_revaluation_get_quants_view.xml",
        "security/stock_inventory_revaluation_security.xml",
        "security/ir.model.access.csv",
        "views/stock_inventory_revaluation_view.xml",
        "views/product_view.xml",
        "views/account_move_line_view.xml",
        "data/stock_inventory_revaluation_data.xml",
        "wizards/stock_inventory_revaluation_mass_post_view.xml",
    ],
    'installable': True,
}
