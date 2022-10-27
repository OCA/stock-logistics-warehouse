# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Stock Available Info Popup",
    "summary": "Adds an 'Available to promise' quantity to the popover shown "
    "in sale order line that display stock info of the product",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale_stock", "stock_available"],
    "data": ["views/sale_order_views.xml"],
    "assets": {
        "web.assets_qweb": [
            "sale_stock_available_info_popup/static/src/xml/qty_at_date.xml",
        ],
    },
    "installable": True,
}
