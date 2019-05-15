# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Orderpoint Manual Procurement Location",
    "summary": "This module allows to set an alternative sublocation to "
               "procure from",
    "version": "11.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": [
        "stock_orderpoint_manual_procurement",
    ],
    "data": ["views/stock_warehouse_orderpoint_view.xml"],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
