import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-stock-logistics-warehouse",
    description="Meta package for oca-stock-logistics-warehouse Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-stock_move_location',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
