# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Non Stocked",
    "summary": "It adds a option to a create a 0 quantity quant for products without any stock and any quants.",
    "version": "16.0.1.0.0",
    "depends": [
        "stock",
        "stock_inventory",
        "stock_inventory_preparation_filter",
    ],
    "author": "Ivan Perez, Coninpe",
    "mantainers": ["linuxivan"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "license": "AGPL-3",
    "data": ["views/stock_inventory_view.xml"],
    "installable": True,
}
