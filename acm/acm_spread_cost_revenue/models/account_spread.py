# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountSpread(models.Model):
    _inherit = 'account.spread'

    def create(self, vals):
        """ Usually, spread will use invoice date,
        but for ACM case, we also enforce using contract start date """
        if vals.get('force_spread_date'):
            vals['spread_date'] = vals['force_spread_date']
            del vals['force_spread_date']
        return super().create(vals)
