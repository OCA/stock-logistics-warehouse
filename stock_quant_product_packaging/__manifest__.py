# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Product Packaging",
    "summary": """
        Add product packaging information on quants""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "views/product_product.xml",
        "security/stock_quant_packaging_info.xml",
        "views/stock_quant_packaging_info.xml",
        "views/stock_quant.xml",
    ],
    "demo": [
        "demo/stock_quant_packaging_info.xml",
    ],
}
