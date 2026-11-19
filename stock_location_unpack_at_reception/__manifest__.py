# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Location Unpack At Reception",
    "summary": "Unpack the packages arriving in a location",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": [
        # Odoo
        "stock",
    ],
    "data": [
        "views/stock_location.xml",
    ],
}
