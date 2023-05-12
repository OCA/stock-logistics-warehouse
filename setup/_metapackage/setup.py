import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_move_line_stock_info>=16.0dev,<16.1dev',
        'odoo-addon-scrap_reason_code>=16.0dev,<16.1dev',
        'odoo-addon-stock_demand_estimate>=16.0dev,<16.1dev',
        'odoo-addon-stock_helper>=16.0dev,<16.1dev',
        'odoo-addon-stock_location_lockdown>=16.0dev,<16.1dev',
        'odoo-addon-stock_location_position>=16.0dev,<16.1dev',
        'odoo-addon-stock_location_product_restriction>=16.0dev,<16.1dev',
        'odoo-addon-stock_location_zone>=16.0dev,<16.1dev',
        'odoo-addon-stock_move_auto_assign>=16.0dev,<16.1dev',
        'odoo-addon-stock_move_auto_assign_auto_release>=16.0dev,<16.1dev',
        'odoo-addon-stock_move_common_dest>=16.0dev,<16.1dev',
        'odoo-addon-stock_move_location>=16.0dev,<16.1dev',
        'odoo-addon-stock_mts_mto_rule>=16.0dev,<16.1dev',
        'odoo-addon-stock_packaging_calculator>=16.0dev,<16.1dev',
        'odoo-addon-stock_picking_commercial_partner>=16.0dev,<16.1dev',
        'odoo-addon-stock_picking_volume>=16.0dev,<16.1dev',
        'odoo-addon-stock_quant_cost_info>=16.0dev,<16.1dev',
        'odoo-addon-stock_reserve>=16.0dev,<16.1dev',
        'odoo-addon-stock_route_mto>=16.0dev,<16.1dev',
        'odoo-addon-stock_search_supplierinfo_code>=16.0dev,<16.1dev',
        'odoo-addon-stock_storage_category_capacity_name>=16.0dev,<16.1dev',
        'odoo-addon-stock_warehouse_calendar>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
