# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Account Manual Adjustment",
    "summary": "Shows in the product inventory stock value and the accounting "
               "value and allows to reconcile them",
    "version": "10.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_account", "stock_inventory_revaluation"],
    "data": [
        "data/stock_valuation_account_manual_adjustment_data.xml",
        "security/stock_valuation_account_manual_adjustment_security.xml",
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/account_move_line_view.xml",
        "views/stock_valuation_account_manual_adjustment_view.xml",
        "wizards/mass_create_view.xml"
    ],
    'pre_init_hook': 'pre_init_hook',
    "license": "AGPL-3",
    'installable': True,
}
