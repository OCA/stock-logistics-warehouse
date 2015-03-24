# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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


def migrate(cr, installed_version):
    """Update a wrong location that is no_update in XML."""
    if installed_version == '8.0.0.1':
        cr.execute('''
            UPDATE stock_location
            SET location_id = (
                SELECT res_id
                FROM ir_model_data
                WHERE name = 'stock_location_locations'
                AND module = 'stock'
            )
            WHERE id = (
                SELECT res_id
                FROM ir_model_data
                WHERE name = 'stock_location_reservation'
                AND module = 'stock_reserve'
            )
            AND location_id = (
                SELECT res_id
                FROM ir_model_data
                WHERE name = 'stock_location_company'
                AND module = 'stock'
            );
        ''')
