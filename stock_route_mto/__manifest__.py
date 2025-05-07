# Copyright 2022 ACSONE SA/NV
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Route Mto",
    "summary": """
        Allows to identify MTO routes through a checkbox and availability to filter
        them.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "maintainers": ["rousseldenis", "jbaudoux"],
    "data": [
        "data/stock_route.xml",
        "views/stock_route.xml",
    ],
    "post_init_hook": "post_init_hook",
}
