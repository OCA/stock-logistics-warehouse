
{
    'name': 'Stock Inventory Import from CSV file',
    'version': "1.0",
    'category': "Generic Modules",
    'description': """
    Wizard to import Inventory from a CSV file
    The file must have at least 2 columns with "code" and "quantity" Head Keys.
    You can also add a third column with Key "location" to add product location
    (if not defined, default inventory location will be used)
    You can also add a fourth column with Key "lot" to add a product lot.
    """,
    'author': 'OdooMRP team',
    'contributors': ["Daniel Campos <danielcampos@avanzosc.es>"],
    'website': "http://www.avanzosc.com",
    'depends': ['stock'],
    'data': ['security/ir.model.access.csv',
             'wizard/import_inventory_view.xml',
             'views/inventory_view.xml'],
    'installable': True,
}
