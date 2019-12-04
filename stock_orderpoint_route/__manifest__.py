# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Orderpoint Route",
    "summary": "Allows to force a route to be used when procuring from "
               "orderpoints",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Eficent, "
              "Camptocamp, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_warehouse_orderpoint_views.xml",
    ],
    "installable": True,
}
