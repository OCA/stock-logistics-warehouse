# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Warehouse Calendar",
    "summary": "Adds a calendar to the Warehouse",
    "version": "12.0.1.0.2",
    "license": "LGPL-3",
    "website": "https://github.com/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": [
        "stock",
        "resource",
    ],
    "data": [
        "views/stock_warehouse_views.xml",
    ],
    "installable": True,
    'development_status': 'Beta',
    'maintainers': ['jbeficent'],
}
