# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Group Reservation Rate",
    "summary": """This module allows to compute the reservation rate
    on a picking group""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock_picking_reservation_rate",
        "stock_picking_type_group",
    ],
    "data": ["views/stock_picking.xml"],
}
