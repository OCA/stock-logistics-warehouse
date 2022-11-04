import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-stock_location_product_restriction>=16.0dev,<16.1dev',
        'odoo-addon-stock_move_auto_assign>=16.0dev,<16.1dev',
        'odoo-addon-stock_mts_mto_rule>=16.0dev,<16.1dev',
        'odoo-addon-stock_warehouse_calendar>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
