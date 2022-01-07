import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_move_line_stock_info>=15.0dev,<15.1dev',
        'odoo-addon-procurement_auto_create_group>=15.0dev,<15.1dev',
        'odoo-addon-stock_demand_estimate>=15.0dev,<15.1dev',
        'odoo-addon-stock_helper>=15.0dev,<15.1dev',
        'odoo-addon-stock_move_location>=15.0dev,<15.1dev',
        'odoo-addon-stock_warehouse_calendar>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
