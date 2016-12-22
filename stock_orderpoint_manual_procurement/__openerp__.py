# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Orderpoint manual procurement",
    "summary": "Allows to create procurement orders from orderpoints instead "
               "of relying only on the scheduler",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["stock",
                "stock_orderpoint_uom"],
    "data": ["security/stock_orderpoint_manual_procurement_security.xml",
             "wizards/make_procurement_orderpoint_view.xml",
             "views/procurement_order_view.xml",
             "views/stock_warehouse_orderpoint_view.xml"
             ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
}
