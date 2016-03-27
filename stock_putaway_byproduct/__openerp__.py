#
{
    'name': 'Putaway strategy per product',
    'summary': 'Set a product location per product',
    'description': """
        This module allows to set a specific stock location per
        product.  On the product form, the case,rack,loc fields are
        replaced with a specific putaway strategy and location id for the
        product.

        A putaway strategy can be used to ensure that incoming products
        will be stored in the location set on the product form.

    """,
    'version': '8.0.0.1',
    'category': 'Inventory',
    'website': 'http://www.apertoso.be',
    'author': 'Apertoso N.V., Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'applicaton': False,
    'installable': True,
    'depends': [
        'product',
        'stock'
    ],
    'data': [
        'views/product.xml',
        'views/product_putaway.xml',
        'security/ir.model.access.csv',
    ],
}
