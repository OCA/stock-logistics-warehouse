# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Template",
    "summary": "Introduces the concept of location template",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_location_template_views.xml",
        "views/stock_location_views.xml",
    ],
}
