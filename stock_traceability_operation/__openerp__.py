# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Traceability with detailed operations",
    "summary": "Adds operations in traceability and quant history",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
    "author": u"Numérigraphe, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "report/report_traceability_operation_view.xml",
        "views/product_product_view.xml",
    ],
    'images': [],
}
