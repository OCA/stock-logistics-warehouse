# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 Tecnativa - Ernesto Tejeda
# 2020 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Lock Lot",
    "Summary": "Restrict blocked lots in Stock Moves and reservations",
    "version": "12.0.1.0.0",
    "author": "Avanzosc, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock", "product"],
    "data": [
        "security/stock_lock_lot_security.xml",
        "data/stock_lock_lot_data.xml",
        "views/product_category_view.xml",
        "views/stock_production_lot_view.xml",
        "views/stock_location_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
