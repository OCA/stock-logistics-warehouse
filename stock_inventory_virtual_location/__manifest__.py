# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Stock Inventory Virtual Location",
    'summary': "Allows to change the virtual location"
               " in inventory adjustments.",
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'category': 'Warehouse',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_inventory_line_view.xml',
        'wizard/stock_product_change_qty.xml',
    ],
    'installable': True,
}
