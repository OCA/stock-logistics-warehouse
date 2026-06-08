# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Request Analytic Tag",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_request", "account_analytic_tag"],
    "maintainers": ["CristianoMafraJunior"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/stock_request_views.xml",
    ],
}
