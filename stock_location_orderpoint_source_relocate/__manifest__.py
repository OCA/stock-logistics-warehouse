# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "stock_location_orderpoint_source_relocate",
    "author": "MT Software, BCIM, Odoo Community Association (OCA)",
    "summary": "Run an auto location orderpoint replenishment "
    "after the move relocation done by Stock Move Source Relocate",
    "version": "14.0.1.0.3",
    "development_status": "Alpha",
    "data": [],
    "depends": [
        "stock_location_orderpoint",
        "stock_move_source_relocate",
    ],
    "license": "AGPL-3",
    "maintainers": ["mt-software-de", "jbaudoux"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
}
