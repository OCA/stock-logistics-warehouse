# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Volume From Packaging",
    "summary": """
        Use volume information on potential product packaging to compute the
        volume of a stock.move""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock_picking_volume",
        "stock_packaging_calculator",
        "product_packaging_dimension",
    ],
    "data": [],
    "demo": [],
}
