# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product - Stock Coverage",
    "version": "12.0.0.0.1",
    "category": "Stock",
    "summary": "Compute estimated stock coverage based on POS sales over "
    "a date range.",
    "author": "Odoo Community Association (OCA), Coop IT Easy SC",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": ["point_of_sale", "stock"],
    "data": ["views/product_template_view.xml", "data/cron.xml"],
    "installable": True,
    "application": False,
}
