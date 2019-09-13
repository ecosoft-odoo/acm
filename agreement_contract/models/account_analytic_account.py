# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
from datetime import datetime


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    update_contract = fields.Char(
        compute='compute_active',
    )

    @api.multi
    def compute_active(self):
        return
        # current_date = datetime.today().strftime('%Y-%m-%d')
        # date_start = str(self.date_start)
        # date_end = str(self.date_end)
        # condition_1 = date_end >= current_date >= date_start
        # condition_2 = self.active is False
        # if condition_1 and condition_2:
        #     self._write({'active': True})

    @api.onchange('recurring_next_date', 'date_start')
    def _onchange_active(self):
        return
        # current_date = datetime.today().strftime('%Y-%m-%d')
        # condition_1 = str(self.date_start) <= current_date
        # condition_2 = self.contract_genre in ['new', 'renew']
        # if condition_1 and condition_2:
        #     self.active = True
        # else:
        #     self.active = False

    @api.multi
    def recurring_create_invoice(self):
        return
        # new_date = super().recurring_create_invoice()
        # if new_date.contract_id.recurring_next_date > self.date_end:
        #     self.active = False
