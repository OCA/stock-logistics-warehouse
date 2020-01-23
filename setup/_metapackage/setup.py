import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_move_line_product',
        'odoo13-addon-account_move_line_stock_info',
        'odoo13-addon-stock_account_change_qty_reason',
        'odoo13-addon-stock_available_unreserved',
        'odoo13-addon-stock_change_qty_reason',
        'odoo13-addon-stock_demand_estimate',
        'odoo13-addon-stock_inventory_chatter',
        'odoo13-addon-stock_inventory_exclude_sublocation',
        'odoo13-addon-stock_inventory_lockdown',
        'odoo13-addon-stock_removal_location_by_priority',
        'odoo13-addon-stock_warehouse_calendar',
        'odoo13-addon-stock_warehouse_orderpoint_stock_info',
        'odoo13-addon-stock_warehouse_orderpoint_stock_info_unreserved',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
