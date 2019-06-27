# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Removal Location by Priority",
    "summary": "Establish a removal priority on stock locations.",
    "version": "12.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": [
        'security/stock_security.xml',
        'views/res_config_settings_views.xml',
        'views/stock_location_view.xml',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    'pre_init_hook': 'pre_init_hook',
}
