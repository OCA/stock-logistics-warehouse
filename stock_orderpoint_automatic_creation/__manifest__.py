# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Orderpoint Automatic Creation",
    "version": "11.0.1.0.0",
    "author": "AvanzOSC, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock",
    ],
    "category": "Inventory",
    "data": [
        "views/res_company_views.xml",
        "views/product_views.xml",
    ],
    "installable": True,
}
