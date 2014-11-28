# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2010-2012 Camptocamp SA
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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
#

{
    "name": "Ignore planned receptions in quantity available to promise",
    "version": "2.0",
    "depends": ["stock_available"],
    "author": "Camptocamp",
    "license": "AGPL-3",
    "description": u"""
Ignore planned receptions in quantity available to promise
----------------------------------------------------------

Normally the quantity available to promise is based on the virtual stock,
which includes both planned outgoing and incoming goods.
This module will subtract the planned receptions from the quantity available to
promise.

Contributors
------------
  * Author: Guewen Baconnier (Camptocamp SA)
  * Sébastien BEAU (Akretion) <sebastien.beau@akretion.com>
  * Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>
""",
    "category": "Hidden",
}
