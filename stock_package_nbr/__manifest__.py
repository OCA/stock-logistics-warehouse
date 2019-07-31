# Copyright 2017 Syvain Van Hoof (Okia) <sylvain@okia.be>
# Copyright 2017-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Package Nbr',
    'version': '12.0.1.0.0',
    'author': "BCIM, Okia, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/stock-logistics-warehouse",
    'summary': "Add quantity of packages in a pack.",
    'category': 'Stock Management',
    'depends': [
        'stock',
    ],
    'data': [
        'wizards/put_in_pack_nbr.xml',
        'views/stock_picking.xml',
        'views/stock_quant_package.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
