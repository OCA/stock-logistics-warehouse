import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_move_line_product>=15.0dev,<15.1dev',
        'odoo-addon-account_move_line_stock_info>=15.0dev,<15.1dev',
        'odoo-addon-procurement_auto_create_group>=15.0dev,<15.1dev',
        'odoo-addon-sale_stock_available_info_popup>=15.0dev,<15.1dev',
        'odoo-addon-stock_archive_constraint>=15.0dev,<15.1dev',
        'odoo-addon-stock_available>=15.0dev,<15.1dev',
        'odoo-addon-stock_available_mrp>=15.0dev,<15.1dev',
        'odoo-addon-stock_available_unreserved>=15.0dev,<15.1dev',
        'odoo-addon-stock_demand_estimate>=15.0dev,<15.1dev',
        'odoo-addon-stock_demand_estimate_matrix>=15.0dev,<15.1dev',
        'odoo-addon-stock_helper>=15.0dev,<15.1dev',
        'odoo-addon-stock_location_lockdown>=15.0dev,<15.1dev',
        'odoo-addon-stock_location_route_description>=15.0dev,<15.1dev',
        'odoo-addon-stock_lot_filter_available>=15.0dev,<15.1dev',
        'odoo-addon-stock_move_location>=15.0dev,<15.1dev',
        'odoo-addon-stock_mts_mto_rule>=15.0dev,<15.1dev',
        'odoo-addon-stock_orderpoint_move_link>=15.0dev,<15.1dev',
        'odoo-addon-stock_orderpoint_purchase_link>=15.0dev,<15.1dev',
        'odoo-addon-stock_orderpoint_uom>=15.0dev,<15.1dev',
        'odoo-addon-stock_packaging_calculator>=15.0dev,<15.1dev',
        'odoo-addon-stock_putaway_product_template>=15.0dev,<15.1dev',
        'odoo-addon-stock_quant_manual_assign>=15.0dev,<15.1dev',
        'odoo-addon-stock_request>=15.0dev,<15.1dev',
        'odoo-addon-stock_request_purchase>=15.0dev,<15.1dev',
        'odoo-addon-stock_secondary_unit>=15.0dev,<15.1dev',
        'odoo-addon-stock_warehouse_calendar>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
