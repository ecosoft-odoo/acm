# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementContractCreate(models.TransientModel):
    _name = 'agreement.contract.create'
    _description = 'Create contract the selected agreement'

    date_start = fields.Date(
        string='Start Date',
        required=True,
    )
    date_end = fields.Date(
        string='End Date',
    )
    recurring_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        required=True,
        help='Repeat every (Days/Week/Month/Year)',
    )
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        string='Recurrence',
        default='monthly',
        required=True,
        help='Specify Interval for automatic invoice generation.',
    )
    contract_genre = fields.Selection(
        [('new', 'New')],
        default='new',
    )

    @api.multi
    def action_create_contract(self):
        self.ensure_one()
        context = dict(self._context or {})
        # Update context
        context.update({
            'date_start': self.date_start,
            'date_end': self.date_end,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type, })
        # Create contract
        agreement_id = context.get('active_id')
        agreement = self.env['agreement'].browse(agreement_id)
        contract = agreement.with_context(context).create_new_contract()
        contract._onchange_active()
        return contract
