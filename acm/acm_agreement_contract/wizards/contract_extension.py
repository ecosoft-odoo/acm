# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractExtension(models.TransientModel):
    _name = 'contract.extension'
    _description = 'Extension contract from agreement'

    date_start = fields.Date(
        string='Start Date',
        required=True,
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
    )
    date_contract = fields.Date(
        string='Contract Date',
        default=fields.Date.today(),
        required=True,
    )
    recurring_interval = fields.Integer(
        string='Repeat Every',
        default=1,
        required=True,
        help='Repeat every (Days/Week/Month/Year)',
    )
    recurring_rule_type = fields.Selection(
        selection=[
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('yearly', 'Year(s)'), ],
        string='Recurrence',
        default='monthly',
        required=True,
        help='Specify Interval for automatic invoice generation.',
    )

    @api.multi
    def action_extension_contract(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(_('"Start Date" cannot be less than "End Date"'))
        context = dict(self._context or {})
        active_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(active_id)
        if agreement.is_contract_create == 'False':
            raise UserError(_('Please create contract.'))
        if agreement.end_date >= self.date_start:
            raise UserError(
                _('The contract is still active on the date you selected.'))
        new_agreement = agreement.with_context({
            'name': ' Extension',
            'partner_id': agreement.partner_id.id,
            'partner_contact_id': agreement.partner_contact_id.id,
            'date_contract': self.date_contract,
            'start_date': self.date_start,
            'end_date': self.date_end,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
            'extension': True,
        })
        return new_agreement._create_agreement()
