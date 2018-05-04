# -*- coding: utf-8 -*-
# Copyright 2016 Avanzosc (<http://www.avanzosc.es>)
# Copyright 2016 Tecnativa (<http://www.tecnativa.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Inventory Import from CSV file",
    "version": "8.0.1.0.0",
    "category": "Warehouse Management",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    "website": "http://www.odoomrp.com",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_inventory_view.xml",
        "views/inventory_view.xml",
    ],
    "installable": True,
}
