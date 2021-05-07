# Copyright 2021 VentorTech OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def compute_over_discrepancy_line_count(cr):

    cr.execute("""
    ALTER TABLE stock_inventory
        ADD COLUMN IF NOT EXISTS over_discrepancy_line_count integer;
    """)

    # stock.inventory.line
    cr.execute("""
    ALTER TABLE stock_inventory_line
        ADD COLUMN IF NOT EXISTS discrepancy_qty numeric;
    """)

    cr.execute("""
    ALTER TABLE stock_inventory_line
        ADD COLUMN IF NOT EXISTS discrepancy_percent numeric;
    """)

    cr.execute("""
    ALTER TABLE stock_inventory_line
        ADD COLUMN IF NOT EXISTS discrepancy_threshold numeric;
    """)

    # stock.location
    cr.execute("""
    ALTER TABLE stock_location
        ADD COLUMN IF NOT EXISTS discrepancy_threshold numeric;
    """)

    cr.execute("""
    UPDATE stock_location sl
        SET discrepancy_threshold = 0;
    """)

    # stock.inventory.line _compute_discrepancy
    # discrepancy_qty field
    cr.execute("""
    UPDATE stock_inventory_line sil
        SET discrepancy_qty = sil.product_qty - sil.theoretical_qty;
    """)

    cr.execute("""
    UPDATE stock_inventory_line sil
        SET discrepancy_percent = CASE WHEN sil.theoretical_qty > 0
            THEN 100 * ABS((sil.product_qty - sil.theoretical_qty) / theoretical_qty)
            WHEN sil.theoretical_qty = 0 AND sil.product_qty > 0
            THEN 100.0
            END;
    """)
