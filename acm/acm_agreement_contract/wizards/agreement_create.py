# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementCreate(models.TransientModel):
    _name = 'agreement.create'
    _description = 'Create Agreement'

    template_ids = fields.Many2many(
        comodel_name='agreement',
        string='Template',
        required=True,
    )
    name = fields.Char(
        readonly=True,
    )
    post_name = fields.Char(
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
    )
    partner_contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner Contact',
        help='The primary partner contact (If Applicable).',
    )
    date_contract = fields.Date(
        string='Contract Date',
        required=True,
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
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)'), ],
        string='Recurrence',
        required=True,
        help='Specify Interval for automatic invoice generation.',
    )
    income_type_id = fields.Many2one(
        comodel_name='agreement.income.type',
        string='Income Type',
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
    )
    show_income_type = fields.Boolean(
        related='company_id.show_income_type',
    )

    @api.onchange('template_ids')
    def _onchange_template_ids(self):
        self.name = '{%s}' % ', '.join(self.template_ids.mapped('name'))

    @api.multi
    def action_create_agreement(self):
        self.ensure_one()
        agreements = self.template_ids.with_context({
            'post_name': self.post_name,
            'partner_id': self.partner_id.id,
            'partner_contact_id': self.partner_contact_id.id,
            'date_contract': self.date_contract,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
            'income_type_id': self.income_type_id.id,
        })
        new_agreements = agreements.create_agreement()
        return new_agreements.view_agreement()
