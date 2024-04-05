# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import hashlib
import struct

from odoo import fields, models


def pg_advisory_lock(env, int_lock: int):
    """Attempts to acquire a Postgres transactional advisory lock.

    Raises an OperationalError LOCK_NOT_AVAILABLE if the lock could not be acquired.
    """
    env.cr.execute(
        """
        DO $$
        BEGIN
            IF NOT pg_try_advisory_xact_lock(%s) THEN
                RAISE EXCEPTION USING
                    MESSAGE = 'Lock not available',
                    ERRCODE = '55P03';
            END IF;
        END $$;
        """,
        (int_lock),
    )


class StockRule(models.Model):
    _inherit = "stock.rule"

    auto_create_group_by_product = fields.Boolean(string="Procurement Group by Product")

    def _get_auto_procurement_group(self, product):
        if self.auto_create_group_by_product:
            if product.auto_create_procurement_group_ids:
                return fields.first(product.auto_create_procurement_group_ids)
            # Make sure that two transactions cannot create a procurement group
            # For the same product at the same time.
            lock_name = f"product.product,{product.id}-auto-proc-group"
            hasher = hashlib.sha1(str(lock_name).encode())
            bigint_lock = struct.unpack("q", hasher.digest()[:8])
            pg_advisory_lock(self.env, bigint_lock)
        return super()._get_auto_procurement_group(product)

    def _prepare_auto_procurement_group_data(self, product):
        result = super()._prepare_auto_procurement_group_data(product)
        if self.auto_create_group_by_product:
            result["product_id"] = product.id
            result["partner_id"] = False
        return result
