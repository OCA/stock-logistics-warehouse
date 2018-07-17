# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging


_logger = logging.getLogger(__name__)

__name__ = "Upgrade to 8.0.2.0.0"


def copy_profile_variability(cr):
    cr.execute("""SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_buffer_profile' AND
        column_name='old_variability'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_buffer_profile
            ADD COLUMN old_variability
            varchar(30);
            COMMENT ON COLUMN stock_buffer_profile.old_variability
            IS 'Old Variability';
            """)
    cr.execute(
        """
        UPDATE stock_buffer_profile as sir
        SET old_variability = variability
        """)


def copy_profile_variability_factor(cr):
    cr.execute("""SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_buffer_profile' AND
        column_name='old_variability_factor'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_buffer_profile
            ADD COLUMN old_variability_factor
            double precision;
            COMMENT ON COLUMN stock_buffer_profile.old_variability_factor
            IS 'Old Variability Factor';
            """)
    cr.execute(
        """
        UPDATE stock_buffer_profile as sir
        SET old_variability_factor = variability_factor
        """)


def copy_profile_lead_time(cr):
    cr.execute("""SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_buffer_profile' AND
        column_name='old_lead_time'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_buffer_profile
            ADD COLUMN old_lead_time
            varchar(30);
            COMMENT ON COLUMN stock_buffer_profile.old_lead_time
            IS 'Old Lead Time';
            """)
    cr.execute(
        """
        UPDATE stock_buffer_profile
        SET old_lead_time = lead_time
        """)


def copy_profile_lead_time_factor(cr):
    cr.execute("""SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_buffer_profile' AND
        column_name='old_lead_time_factor'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_buffer_profile
            ADD COLUMN old_lead_time_factor
            double precision;
            COMMENT ON COLUMN stock_buffer_profile.old_lead_time_factor
            IS 'Old Lead Time Factor';
            """)
    cr.execute(
        """
        UPDATE stock_buffer_profile as sir
        SET old_lead_time_factor = lead_time_factor
        """)


def migrate(cr, version):
    if not version:
        return
    copy_profile_variability(cr)
    copy_profile_variability_factor(cr)
    copy_profile_lead_time(cr)
    copy_profile_lead_time_factor(cr)
