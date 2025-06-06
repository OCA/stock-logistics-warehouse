# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Move Stock Reset Quantity",
    "version": "18.0.1.0.0",
    "author": "BCIM, Odoo Community Association (OCA)",
    "summary": "Reset quantity to zero",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": ["stock"],
    "category": "Stock",
    "data": [
        "views/stock_move_line.xml",
        "views/stock_picking.xml",
    ],
}
