# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Portal Stock Location Content Template",
    "summary": """ This module allows your portal users
            to access and complete their assigned checks from the portal.""",
    "version": "14.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainers": ["max3903"],
    "license": "AGPL-3",
    "depends": ["portal", "stock_location_content_template"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/portal_view.xml",
        "views/stock_location_content_views.xml",
    ],
}
