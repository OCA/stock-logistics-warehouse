# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Stock Inventory Virtual Location Change Quantity Reason",
    'summary': "Glue module",
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'category': 'Warehouse',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'stock_change_qty_reason', 'stock_inventory_virtual_location',
    ],
    'data': [
        'views/stock_inventory_line_reason_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
