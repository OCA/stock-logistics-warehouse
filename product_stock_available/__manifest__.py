{
    'name': 'Product Stock Available',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'summary': 'Add available Warehouses and Locations info and filter to Products',
    'description': """
        Adds a many2many field to product.product to filter by available Warehouses and Locations.
        Updates the field when stock moves are processed.
    """,
    'author': 'Stefano Consolaro-Integral Solutions, Odoo Community Association (OCA)',
    'website': 'https://www.integralsolutions.it',
    'license': 'AGPL-3',
    'depends': [
        # OCB dependencies
        'product',
        'stock'
        ],
    'data': [
        'views/product_views.xml',
        'views/stock_views.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
