# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import pooler
from openerp import SUPERUSER_ID
import logging


_logger = logging.getLogger(__name__)

__name__ = "Upgrade to 8.0.2.0.0"


def migrate_variability(cr):
    pool = pooler.get_pool(cr.dbname)
    variability_obj = pool['stock.buffer.profile.variability']
    cr.execute("""
        SELECT old_variability, old_variability_factor
        FROM stock_buffer_profile
        WHERE old_variability IS NOT NULL
        AND old_variability_factor IS NOT NULL
        GROUP by old_variability, old_variability_factor""")
    for variability, variability_factor in cr.fetchall():
        var_id = variability_obj.create(cr, SUPERUSER_ID, {
            'name': variability,
            'factor': variability_factor
        })
        cr.execute("""
        UPDATE stock_buffer_profile
        SET variability_id = %s
        WHERE old_variability_factor = %s
        AND old_variability = '%s'""" % (var_id, variability_factor,
                                         variability))


def migrate_lead_time(cr):
    pool = pooler.get_pool(cr.dbname)
    lead_time_obj = pool['stock.buffer.profile.lead.time']
    cr.execute("""
        SELECT old_lead_time, old_lead_time_factor
        FROM stock_buffer_profile
        WHERE old_lead_time IS NOT NULL
        AND old_lead_time_factor IS NOT NULL
        GROUP by old_lead_time, old_lead_time_factor""")
    for lead_time, lead_time_factor in cr.fetchall():
        lt_id = lead_time_obj.create(cr, SUPERUSER_ID, {
            'name': lead_time,
            'factor': lead_time_factor
        })
        cr.execute("""
        UPDATE stock_buffer_profile
        SET lead_time_id = %s
        WHERE old_lead_time_factor = %s
        AND old_lead_time = '%s'""" % (lt_id, lead_time_factor, lead_time))


def run_cron_ddmrp(cr):
    pool = pooler.get_pool(cr.dbname)
    pool['stock.warehouse.orderpoint'].cron_ddmrp(cr, SUPERUSER_ID,
                                                  automatic=True)


def migrate(cr, version):
    if not version:
        return
    migrate_variability(cr)
    migrate_lead_time(cr)

