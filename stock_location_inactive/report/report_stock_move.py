# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, orm
from openerp import tools


class ReportStockMove(orm.Model):

    """
    Subclass report.stock.inventory model.

    Extend the model report.stock.inventory to add a filter in location to check if
    the stock location is disable
    """

    _name = "report.stock.inventory"
    _inherit = "report.stock.inventory"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_stock_inventory')
        cr.execute("""
            CREATE OR REPLACE view report_stock_inventory AS (
        (SELECT
            min(m.id) as id, m.date as date,
            to_char(m.date, 'YYYY') as year,
            to_char(m.date, 'MM') as month,
            m.partner_id as partner_id, m.location_id as location_id,
            m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,
            m.company_id,
            m.state as state, m.prodlot_id as prodlot_id,

            coalesce(sum(-pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
            coalesce(sum(-m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty
        FROM
            stock_move m
                LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                LEFT JOIN product_product pp ON (m.product_id=pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
                LEFT JOIN product_uom u ON (m.product_uom=u.id)
                LEFT JOIN stock_location l ON (m.location_id=l.id)
                WHERE m.state != 'cancel' and l.active is True
        GROUP BY
            m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id,
            m.location_id,  m.location_dest_id, m.prodlot_id, m.date, m.state,
            l.usage, l.scrap_location, m.company_id, pt.uom_id,
            to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
        ) UNION ALL (
        SELECT
            -m.id as id, m.date as date,
            to_char(m.date, 'YYYY') as year,
            to_char(m.date, 'MM') as month,
            m.partner_id as partner_id, m.location_dest_id as location_id,
            m.product_id as product_id, pt.categ_id as product_categ_id,
            l.usage as location_type, l.scrap_location as scrap_location,
            m.company_id,
            m.state as state, m.prodlot_id as prodlot_id,
            coalesce(sum(pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
            coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty
        FROM
            stock_move m
                LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                LEFT JOIN product_product pp ON (m.product_id=pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
                LEFT JOIN product_uom u ON (m.product_uom=u.id)
                LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
                WHERE m.state != 'cancel' and l.active is True
        GROUP BY
            m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id,
            m.location_id, m.location_dest_id,m.prodlot_id, m.date, m.state,
            l.usage, l.scrap_location, m.company_id, pt.uom_id,
            to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
            )
        );
        """)
