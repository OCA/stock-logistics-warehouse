# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Dimension",
    "summary": "Allow adding picking dimensions information.",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Delivery",
    "depends": [
        "stock_picking_volume",
    ],
    "data": [
        "views/stock_picking_form.xml",
        "views/report_delivery_document.xml",
    ],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
}
