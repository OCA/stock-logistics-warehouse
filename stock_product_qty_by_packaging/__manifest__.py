# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock packaging calculator",
    "summary": "Compute product quantity to pick by packaging",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_packaging_calculator", "stock"],
    "data": ["views/stock_picking.xml", "views/stock_inventory_line.xml"],
}
