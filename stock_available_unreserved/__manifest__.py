# Copyright 2018 Camptocamp SA
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Available Unreserved",
    "summary": "Quantity of stock available for immediate use",
    "version": "12.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_quant_view.xml",
        "views/product_view.xml",
    ],
    "license": "AGPL-3",
}
