# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Stock Warehouse Lock Location",
    "summary": "Lock location on warehouses, left out of the forecast",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "LGPL-3",
    "depends": [
        # Odoo
        "stock",
    ],
    "data": [
        "views/stock_warehouse.xml",
    ],
    "post_init_hook": "post_init_hook",
}
