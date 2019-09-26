# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementCreate(models.TransientModel):
    _name = 'agreement.create'
    _description = 'Create Agreement at the same time'

    title = fields.Char()
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
    )
    date_contract = fields.Date(
        string='Contract Date',
        default=fields.Date.today(),
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
    )
    date_end = fields.Date(
        string='End Date',
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
    def action_create_agreement(self):
        self.ensure_one()
        agreement_id = self._context.get('active_id')
        template_agreement = self.env['agreement'].browse(agreement_id)
        agreement = template_agreement.with_context({
            'name': self.title,
            'partner_id': self.partner_id.id,
            'date_contract': self.date_contract,
            'start_date': self.date_start,
            'end_date': self.date_end,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
        })
        return agreement._create_agreement()
