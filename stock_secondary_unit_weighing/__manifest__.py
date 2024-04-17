# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighing assistant and secondary units",
    "summary": "Show secondary unit info in the weighing assistant",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock_weighing",
        "stock_secondary_unit",
    ],
    "data": ["views/stock_move_views.xml"],
}
