# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Move Location Dest Constraints Base",
    "summary": "Base module to constrain dest location on stock move line",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_putaway_rule",
    ],
    "data": [
        "data/stock_location.xml",
        "views/stock_location.xml",
    ],
}
