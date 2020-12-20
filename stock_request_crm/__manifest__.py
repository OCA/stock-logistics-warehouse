# Copyright 2020 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request for CRM",
    "summary": "Create stock requests from CRM",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock_request_partner", "crm"],
    "data": [
        "views/crm_lead_views.xml",
        "views/stock_request_view.xml",
        "security/security.xml",
    ],
}
