# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Exclude Sublocation",
    "summary": "Allow to perform inventories of a location without including "
               "its child locations.",
    "version": "11.0.1.0.0",
    "development_status": "Mature",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock", "stock_inventory_chatter"],
    "data": [
        'views/stock_inventory_view.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
