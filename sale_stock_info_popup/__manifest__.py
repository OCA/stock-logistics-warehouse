# Copyright 2020 Tecnativa - Ernesto Tejeda
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Sale Stock Info Popup",
    "summary": "Adds a popover in sale order line to display "
               "stock info of the product",
    "author": "Odoo S.A., Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Sales",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/assets.xml",
        "views/sale_order_views.xml",
    ],
    "qweb": [
        "static/src/xml/qty_at_date.xml",
    ],
    "installable": True,
}
