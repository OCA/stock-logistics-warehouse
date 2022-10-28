# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Warehouse Calendar",
    "summary": "Adds a calendar to the Warehouse",
    "version": "11.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": [
        "stock",
        "resource"
    ],
    "data": [
        "views/stock_warehouse_views.xml",
    ],
    "installable": True,
    'development_status': 'Beta',
    'maintainers': ['jbeficent'],
}
