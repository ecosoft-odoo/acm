# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementCreate(models.TransientModel):
    _name = 'agreement.create'
    _description = 'Create Agreement'

    template_id = fields.Many2one(
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
        required=True,
        index=True,
    )

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.update({
                "name": self.template_id.name,
                "income_type_id": self.template_id.income_type_id,
            })

    @api.multi
    def action_create_agreement(self):
        self.ensure_one()
        agreement = self.template_id.with_context({
            'name': '%s %s' % (self.name, self.post_name),
            'partner_id': self.partner_id.id,
            'partner_contact_id': self.partner_contact_id.id,
            'date_contract': self.date_contract,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
            'income_type_id': self.income_type_id.id,
        })
        new_agreement = agreement.create_agreement()
        return new_agreement.view_agreement()
