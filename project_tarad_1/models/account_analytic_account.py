# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, api
from datetime import datetime


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    contract_create_type = fields.Selection(
        [("new", "New"),
         ("renew", "Renew"),
         ("reject", "Reject"),
         ("violate", "Violate"),
         ("transfer", "Transfer"),
         ],
        readonly=True,
    )
    description = fields.Text(
        string="Description",
        track_visibility="onchange",
        help="Description of the agreement",
    )
    cancel_date = fields.Date(
        string="Cancel Date",
    )

    # @api.onchange('current_date')
    # def _onchange_active(self):
    #     if str(self.date_start) > datetime.today().strftime('%Y-%m-%d'):
    #         self.active = False
    #     else:
    #         self.active = True
