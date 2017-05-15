# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Available Unreserved",
    "summary": "Quantity of stock available for immediate use",
    "version": "10.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": ["views/stock_quant_view.xml",
             "views/product_view.xml"
             ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
