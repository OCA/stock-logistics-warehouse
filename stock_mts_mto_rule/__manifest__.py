# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Stock MTS+MTO Rule',
 'version': '11.0.1.0.0',
 'author': 'Akretion,Odoo Community Association (OCA)',
 'website': 'http://www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Warehouse',
 'summary': 'Add a MTS+MTO route',
 'depends': ['stock',
             ],
 'demo': [],
 'data': ['data/stock_data.xml',
          'view/pull_rule.xml',
          'view/warehouse.xml',
          ],
 'installable': True,
 }
