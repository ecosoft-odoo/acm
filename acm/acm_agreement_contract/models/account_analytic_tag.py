# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api

class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"
    _order = "year desc"

    year = fields.Selection(
        selection=lambda self: self._get_selection_year(),
        string='Year',
    )

    @api.model
    def _get_selection_year(self):
        year_selection = [(str(year), str(year)) for year in range(2020, 2060)]
        return year_selection
