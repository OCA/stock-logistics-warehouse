{
    "name": "Stock Location History",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "depends": ["stock"],
    "category": "Stock",
    "data": [
        # "data/stock_location_stage_data.xml",
        "security/ir.model.access.csv",
        "views/stock_location_views.xml",
        "views/stock_location_stage_views.xml",
        "views/stock_location_history_views.xml",
        "views/stock_lot_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["jasiel-OSI"],
}
