# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_160


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_160.fill_analytic_distribution(
        env,
        table="stock_request",
        analytic_account_column="analytic_account_id",
    )
