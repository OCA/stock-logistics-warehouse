# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock - Manual assignment of quants",
    "version": "8.0.1.2.1",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Ana Juaristi Olalde <anajuaristi@avanzosc.es>",
        "Pedro Manuel Baeza Romero <pedro.baeza@serviciosbaeza.com>"
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "stock",
    ],
    "data": [
        "wizard/assign_manual_quants_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
