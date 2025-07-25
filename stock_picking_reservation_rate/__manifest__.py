# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Reservation Rate",
    "summary": """This module allows to get the reservation rate on the
    picking and to get also the reservation rate from pickings flow""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock",
        "web_widget_progressbar_gradient",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
