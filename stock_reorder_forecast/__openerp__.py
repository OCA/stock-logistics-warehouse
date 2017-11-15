# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock reorder forecast",
    "version": "9.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Stock",
    "summary": "Predict date stock levels will reach minimum and trigger RFQ",
    "depends": [
        'sale',
        'purchase'
    ],
    "demo": [
        'demo/data.xml',
    ],
    "data": [
        'data/ir_config_parameter.xml',
        'wizards/purchase_wizard.xml',
        'wizards/purchase_supplier_wizard.xml',
        'views/product_product.xml',
        "views/product_template.xml",
        'views/product_supplierinfo.xml',
        'views/product_category.xml',
        'views/partner_view.xml',
        'data/cron.xml',
    ],
    "installable": True,
}
