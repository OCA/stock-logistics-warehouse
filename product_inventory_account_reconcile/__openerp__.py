# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Inventory Account Reconcile",
    "summary": "Shows in the product inventory stock value and the accounting "
               "value and allows to reconcile them",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_account"],
    "data": [
        "security/product_inventory_account_reconcile_security.xml",
        "views/product_view.xml",
        "wizards/product_inventory_account_reconcile_view.xml"
    ],
    "license": "AGPL-3",
    'installable': True,
}
