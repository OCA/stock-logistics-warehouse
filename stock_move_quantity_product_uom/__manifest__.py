# Copyright 2025 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Move Quantity Product UOM",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "summary": "computes stock.move's quantity in the uom of the product.",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "installable": True,
    "pre_init_hook": "pre_init_quantity_product_uom",
    "post_init_hook": "post_init_quantity_product_uom",
}
