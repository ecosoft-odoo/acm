# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, api
from datetime import datetime


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    contract_genre = fields.Selection(
        [("new", "New"),
         ("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        default='new',
        readonly=True,
    )
    description = fields.Text(
        string="Description",
        track_visibility="onchange",
        help="Description of the agreement",
    )
    reject_date = fields.Date(
        string="Reject Date",
    )
    violate_date = fields.Date(
        string="Violate Date",
    )
    update_contract = fields.Char(
        compute="compute_active",
    )
    renew_contract_id = fields.Many2one(
        comodel_name="account.analytic.account",
        readonly=True,
    )

    @api.multi
    def compute_active(self):
        current_date = datetime.today().strftime('%Y-%m-%d')
        date_start = str(self.date_start)
        date_end = str(self.date_end)
        next_invoice = str(self.recurring_create_invoice)
        condition_1 = date_end >= current_date >= date_start
        condition_2 = next_invoice <= date_end
        condition_3 = self.active is False
        if condition_1 and condition_2 and condition_3:
            self._write({'active': True})

    @api.onchange('recurring_next_date', 'date_end', 'date_start')
    def _onchange_active(self):
        current_date = datetime.today().strftime('%Y-%m-%d')
        condition_1 = self.recurring_next_date <= self.date_end
        condition_2 = str(self.date_start) <= current_date
        condition_3 = self.contract_genre in ['new', 'renew']
        if condition_1 and condition_2 and condition_3:
            self.active = True
        else:
            self.active = False

    @api.multi
    def recurring_create_invoice(self):
        new_date = super().recurring_create_invoice()
        if new_date.contract_id.recurring_next_date > self.date_end:
            self.active = False
