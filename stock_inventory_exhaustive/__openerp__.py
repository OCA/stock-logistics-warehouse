# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Exhaustive Stock Inventories",
    "summary": "Remove from the stock what is not in the Physical Inventory.",
    "version": "8.0.1.0.0",
    "depends": ["stock"],
    "author": u"Numérigraphe,Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "data": [
        "views/stock_inventory_view.xml",
        "wizard/stock_confirm_uninventoried_location.xml",
    ],
    "images": [
        "images/inventory_form.png",
        "images/inventory_empty_locations.png",
    ],
    'license': 'AGPL-3',
    "installable": True,
}
