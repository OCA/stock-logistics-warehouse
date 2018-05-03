# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Inventory Chatter',
    'version': '11.0.1.0.0',
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    'category': 'Warehouse',
    'summary': "Log changes being done in Inventory Adjustments",
    'depends': ['stock'],
    "data": [
        'data/stock_data.xml',
        'views/stock_inventory_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
