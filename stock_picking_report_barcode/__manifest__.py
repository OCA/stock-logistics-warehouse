# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Report Barcode",
    "summary": "Display the picking barcode on the delivery slip report",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock_picking_form_barcode"],
    "data": [
        "views/stock_picking_type.xml",
        "reports/report_deliveryslip.xml",
    ],
}
