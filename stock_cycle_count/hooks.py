# Copyright 2021 VentorTech OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def compute_inventory_accuracy(cr):
    cr.execute("""
    ALTER TABLE stock_inventory
        ADD COLUMN IF NOT EXISTS inventory_accuracy numeric;
    """)

    cr.execute("""
    UPDATE stock_inventory
        SET inventory_accuracy = 100
    FROM stock_inventory si
    LEFT JOIN stock_inventory_line sil
        ON si.id = sil.inventory_id
    WHERE sil.inventory_id IS NULL AND si.state = 'done'
    """)

    cr.execute("""
    WITH data AS (
        SELECT SUM(ABS(sil.theoretical_qty)) AS theoretical,
            SUM(ABS(sil.discrepancy_qty)) AS abs_discrepancy,
            sil.inventory_id AS inventory_id
        FROM stock_inventory_line sil
        INNER JOIN stock_inventory si
            ON si.id = sil.inventory_id
        GROUP BY sil.inventory_id
    )
    UPDATE stock_inventory_line sil
        SET discrepancy_percent = CASE WHEN theoretical_qty > 0
            THEN 100 * ABS((sil.product_qty - sil.theoretical_qty) / theoretical_qty)
            ELSE 0
            END;
    """)
