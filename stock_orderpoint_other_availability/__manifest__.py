#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Orderpoint other availability",
    "summary": "Compute Minimum Inventory Rule for one product "
               "on availability of another product in another location",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse"
               "/tree/12.0/stock_orderpoint_other_availability",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base",
        "stock",
    ],
    "data": [
        "views/stock_warehouse_orderpoint_views.xml",
    ],
}
