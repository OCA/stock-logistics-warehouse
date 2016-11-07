# -*- coding: utf-8 -*-
# Copyright 2016 OdooMRP Team
# Copyright 2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Reordering rules stock info",
    "version": "8.0.1.0.0",
    "depends": [
        "stock",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "category": "Warehouse",
    "license": "AGPL-3",
    "data": [
        "views/stock_warehouse_orderpoint_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
