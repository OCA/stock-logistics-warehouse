{
    "name": "Stock Picking Product Interchangeable",
    "summary": """Stock Picking Product Interchangeable""",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["CetmixGitDrone"],
    "depends": ["stock_available"],
    "images": ["static/description/banner.png"],
    "data": [
        "views/product_views.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": [
        "demo/product_demo.xml",
        "demo/stock_demo.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
