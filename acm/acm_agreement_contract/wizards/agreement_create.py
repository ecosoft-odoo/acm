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
        # default=fields.Date.today(),
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
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('yearly', 'Year(s)'), ],
        string='Recurrence',
        required=True,
        help='Specify Interval for automatic invoice generation.',
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
        })
        new_agreements = agreements.create_agreement()
        # Write Child Agreements
        for new_agreement in new_agreements:
            child_templates = new_agreement.template_id.child_agreements_ids
            if not child_templates:
                continue
            child_agreements = new_agreements.filtered(
                lambda l: l.template_id in child_templates)
            if child_agreements:
                self._cr.execute("""
                    update agreement set parent_agreement_id = %s
                    where id in %s""", (
                        new_agreement.id,
                        tuple(child_agreements.ids)))
        return new_agreements.view_agreement()
