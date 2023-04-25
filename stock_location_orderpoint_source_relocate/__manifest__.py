# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "stock_location_orderpoint_source_relocate",
    "author": "MT Software, Odoo Community Association (OCA)",
    "summary": "Run an auto location orderpoint replenishment "
    "also after a move gets relocated by Stock Move Source Relocate",
    "version": "14.0.1.0.1",
    "development_status": "Alpha",
    "data": [],
    "depends": [
        "stock_location_orderpoint",
        "stock_move_source_relocate",
    ],
    "license": "AGPL-3",
    "maintainers": ["mt-software-de"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
}
