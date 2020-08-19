# Copyright 2018 Camptocamp SA
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Available Unreserved",
    "summary": "Quantity of stock available for immediate use",
    "version": "12.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_quant_view.xml",
        "views/product_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "license": "LGPL-3",
}
