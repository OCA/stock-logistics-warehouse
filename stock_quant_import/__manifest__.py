{
    "name": "Stock Quantity Import",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Wizard to allow adjusting stock quantities via csv file",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "PyTech SRL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_import_views.xml",
    ],
    "demo": [],
    "maintainers": ["aleuffre", "PicchiSeba", "renda-dev"],
}
