# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        """
    INSERT INTO stock_picking_type_stock_reserve_rule_rel
      (stock_reserve_rule_id, stock_picking_type_id)
    SELECT id, picking_type_id
    FROM stock_reserve_rule
    WHERE picking_type_id IS NOT NULL
    ON CONFLICT DO NOTHING;
    """
    )
