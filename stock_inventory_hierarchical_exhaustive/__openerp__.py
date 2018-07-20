# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Exhaustive and hierarchical inventory adjustments",
    "summary": "Extra consistency checks",
    "version": "8.0.1.0.0",
    "author": u"Numérigraphe,Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "data": [
        "views/stock_inventory_view.xml",
        "wizard/generate_inventory_view.xml",
    ],
    "depends": [
        "stock_inventory_hierarchical",
        "stock_inventory_exhaustive",
    ],
    "auto_install": True,
    'license': 'AGPL-3',
    "installable": True,
}
