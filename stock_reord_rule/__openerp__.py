# -*- encoding: utf-8 -*-
##############################################################################
#
#    Improved reordering rules for OpenERP
#    Copyright (C) 2012 Sergio Corato (<http://www.icstools.it>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Improved reordering rules',
    'version': '0.2',
    'category': 'Tools',
    'description': """
    This module allows to improve reordering rules of stock module.
    
    It works forecasting the stock needed per product for n days of sales, with the next formula:
    (( Qty sold in days_stats * (1+forecast_gap)) / days_stats * days_warehouse)
    where:
    - days_stats = days on wich calculate sales stats;
    - forecast_gap = forecast of increase/decrease on sales (%);
    - days_warehouse = days of stock to keep in the warehouse.""",
    'author': 'Sergio Corato',
    'website': 'http://www.icstools.it',
    'depends': ['procurement','sale',],
    'demo_xml' : [],
    'data': ['stock_reord_rule_view.xml','cron_data.xml',],
    'images': [],
    'active': False,
    'installable': True,
}
