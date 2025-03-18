# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Route Profile",
    "summary": "Add Route profile concept on product",
    "version": "16.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/route_profile.xml",
        "views/product_template.xml",
        "security/ir.model.access.csv",
    ],
    "post_init_hook": "post_init_hook",
}
