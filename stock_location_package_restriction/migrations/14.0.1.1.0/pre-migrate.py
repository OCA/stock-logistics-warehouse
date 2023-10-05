# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def migrate(cr, installed_version):
    if not installed_version:
        return
    # Replace the norestriction value to null for the package_restriction field
    queries = [
        """
            ALTER TABLE stock_location
            ALTER COLUMN package_restriction
            drop not null;
        """,
        """
            UPDATE stock_location
            SET package_restriction = null
            WHERE package_restriction = 'norestriction'
        """,
    ]
    for query in queries:
        cr.execute(query)
