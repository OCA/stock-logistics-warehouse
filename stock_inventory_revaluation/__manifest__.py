# Copyright 2020 Matt Taylor
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Revaluation",
    "summary": "Introduces inventory revaluation as single point to change "
               "the valuation of products.",
    "version": "12.0.1.0.1",
    "development_status": "Production/Stable",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Serpent Consulting Services Pvt. Ltd., "
              "Matt Taylor, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_account", "product"],
    "license": "AGPL-3",
    "data": [
        "wizards/stock_inventory_revaluation_get_moves_view.xml",
        "security/stock_inventory_revaluation_security.xml",
        "security/ir.model.access.csv",
        "views/stock_inventory_revaluation_view.xml",
        "views/stock_inventory_revaluation_template_view.xml",
        "views/product_view.xml",
        "views/account_move_line_view.xml",
        "data/stock_inventory_revaluation_data.xml",
        "wizards/stock_inventory_revaluation_mass_post_view.xml",
    ],
    'installable': True,
}
