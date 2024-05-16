# Copyright (C) 2019 Akretion
# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Warehouse relationship",
    "summary": "Technical module to add warehouse_id field on various stock.* models",
    "version": "14.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Akretion, Pierre Verkest, Odoo Community Association (OCA)",
    "maintainers": ["petrus-v"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
        "stock_location_warehouse",
    ],
    "data": [
        "views/stock_move_line.xml",
        "views/stock_move.xml",
        "views/stock_quant_package.xml",
        "views/stock_quant.xml",
    ],
    "development_status": "Alpha",
}
