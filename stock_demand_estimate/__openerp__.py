# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Demand Estimate",
    "summary": "Allows to create demand estimates.",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["stock",
                "web_widget_x2many_2d_matrix"
                ],
    "data": ["security/ir.model.access.csv",
             "security/stock_security.xml",
             "views/stock_demand_estimate_period_view.xml",
             "views/stock_demand_estimate_view.xml",
             "wizards/stock_demand_estimate_wizard_view.xml",
             ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
}
