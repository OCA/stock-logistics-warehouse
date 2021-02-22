import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-stock_available',
        'odoo14-addon-stock_demand_estimate',
        'odoo14-addon-stock_free_quantity',
        'odoo14-addon-stock_inventory_include_exhausted',
        'odoo14-addon-stock_location_children',
        'odoo14-addon-stock_location_lockdown',
        'odoo14-addon-stock_move_location',
        'odoo14-addon-stock_packaging_calculator',
        'odoo14-addon-stock_warehouse_calendar',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
