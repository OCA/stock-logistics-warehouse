# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Account Inventory Force Date",
    "summary": "Force the inventory adjustments to a date in the past.",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "license": "AGPL-3",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock_account", "stock"],
    "data": [
        "security/stock_account_inventory_force_date_security.xml",
        "views/stock_inventory_view.xml",
        "views/res_company_view.xml",
    ],
    "installable": True,
}
