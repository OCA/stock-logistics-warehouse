# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # Remove jobs previous to the migration
    cr.execute("""
        DELETE FROM queue_job
    """)
    # Remove functions
    cr.execute("""
        DELETE FROM queue_job_function
        WHERE name ILIKE '%openerp%'
    """)
