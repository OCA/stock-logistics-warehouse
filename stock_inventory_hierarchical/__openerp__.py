# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Hierarchical Inventory adjustments",
    "summary": "Group several Inventory adjustments in a master inventory",
    "version": "8.0.2.0.0",
    "depends": ["stock"],
    "author": u"Numérigraphe,Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "data": ["views/stock_inventory_view.xml",
             "wizard/generate_inventory_view.xml"],
    "images": ["images/inventory_form.png",
               "images/inventory_form_actions.png",
               "images/wizard.png"],
    'license': 'AGPL-3',
    'installable': True
}
