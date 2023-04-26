# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "stock_reserve_sale_with_outgoing_moves",
    "summary": "Add process to reserve a sale.order by an outgoing picking",
    "version": "14.0.1.0.0",
    "author": "MT Software, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": [
        "views/sale_views.xml",
    ],
    "depends": [
        "stock_helper",
        "sale_stock",
    ],
    "maintainers": ["mt-software-de"],
    "license": "LGPL-3",
}
