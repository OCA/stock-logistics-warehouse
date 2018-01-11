# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Procurement Auto Create Group",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Allows to configure the system to propose automatically new "
               "procurement groups in procurement orders.",
    "depends": [
        "procurement",
    ],
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "data": [
        'views/procurement_view.xml',
    ],
    "installable": True,
}
