# Copyright 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Automatic Workflow: Reserve Sale stock",
    "version": "13.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "FactorLibre, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow", "stock_reserve_sale"],
    "data": ["views/sale_workflow_process_view.xml"],
    "maintainers": ["CarlosRoca13"],
    "installable": True,
}
