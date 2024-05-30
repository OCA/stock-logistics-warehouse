# Copyright 2022 ForgeFlow S.L.
#   (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Move Reservation Info MRP",
    "summary": "Allows to see the manufacturing order related to the reserved info of Products",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Generic",
    "depends": ["stock_quant_reservation_info", "mrp"],
    "license": "AGPL-3",
    "data": ["views/stock_move_line.xml"],
    "installable": True,
    "auto_install": True,
}
