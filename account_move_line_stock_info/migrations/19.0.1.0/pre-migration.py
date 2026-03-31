def migrate(cr, version):
    # Example: remove obsolete field
    cr.execute("""
        ALTER TABLE stock_move
        DROP COLUMN IF EXISTS old_field
    """)