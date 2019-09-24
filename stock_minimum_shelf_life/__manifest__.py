# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock minimum shelf life",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Allows to set a minimum date in procurement group to force the"
               " reservation mecanism to take only product that expiry date is"
               " after the minimum date.",
    "author": "Camptocamp,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": [
        "stock",
        "product_expiry",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "development_status": 'Alpha',
}
