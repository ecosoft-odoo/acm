# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementCreate(models.TransientModel):
    _name = 'agreement.create'
    _description = 'Create Agreement at the same time'

    title = fields.Char(
        string='Title',
    )
    partner_id = fields.Many2one(
        'res.partner',
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
        [('daily', 'Day(s)'),
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
    def get_default_vals(self):
        self.ensure_one()
        return {
            'name': 'NEW',
            'active': True,
            'version': 1,
            'revision': 0,
            'state': 'draft',
            'stage_id': self.env.ref('agreement_legal.agreement_stage_new').id,
            'partner_id': self.partner_id.id,
            'date_contract': self.date_contract,
            'start_date': self.date_start,
            'end_date': self.date_end,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
            'parent_agreement_id': False,
        }

    @api.multi
    def action_create_agreement(self):
        self.ensure_one()
        agreement_id = self._context.get('active_id')
        template_agreement = self.env['agreement'].browse(agreement_id)
        default_vals = self.get_default_vals()
        default_vals['name'] = template_agreement.name + ' - %s' % self.title
        # Create agreemnt
        new_agreement = template_agreement.copy(default=default_vals)
        new_agreement.sections_ids.mapped('clauses_ids').write({
            'agreement_id': new_agreement.id})
        # Create child agreement
        default_vals['parent_agreement_id'] = new_agreement.id
        for child in template_agreement.child_agreements_ids:
            default_vals['name'] = child.name + ' - %s' % self.title
            child_agreement = child.copy(default=default_vals)
            child_agreement.sections_ids.mapped('clauses_ids').write({
                'agreement_id': child_agreement.id})
        return {
            'res_model': 'agreement',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_agreement.id,
        }
