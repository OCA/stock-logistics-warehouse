# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Products Merge",
    "summary": "Merge duplicate products",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "category": "Sales/Sales",
    "depends": ["product"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizard/base_product_merge_view.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
    "maintainers": ["JasminSForgeFlow"],
}
