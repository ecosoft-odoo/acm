# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from num2words import num2words


class Agreement(models.Model):
    _inherit = 'agreement'

    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer Contract'),
            ('purchase', 'Supplier Contract'), ],
        default='sale',
        required=True,
    )
    is_contract_create = fields.Boolean(
        compute='_compute_is_contract_create',
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
    date_contract = fields.Date(
        string='Contract Date',
        default=fields.date.today(),
    )
    breach_date = fields.Date(
        string='Breach Date',
    )
    extension_agreement_id = fields.Many2one(
        'agreement',
        string="Source Agreement",
        readonly=True,
    )
    transfer_agreement_id = fields.Many2one(
        'agreement',
        string='Agreement',
        readonly=True,
    )
    breach_reason = fields.Text()
    terminate_reason = fields.Text()

    @api.multi
    def trans_months(self, month):
        months = {
            '01': 'มกราคม',
            '02': 'กุมภาพันธ์',
            '03': 'มีนาคม',
            '04': 'เมษายน',
            '05': 'พฤษภาคม',
            '06': 'มิถุนายน',
            '07': 'กรกฎาคม',
            '08': 'สิงหาคม',
            '09': 'กันยายน',
            '10': 'ตุลาคม',
            '11': 'พฤศจิกายน',
            '12': 'ธันวาคม',
        }
        return months[month]

    @api.multi
    def trans_recurring(self, type):
        types = {
            'daily': 'รายวัน',
            'weekly': 'รายสัปดาห์',
            'monthly': 'รายเดือน',
            'monthlylastday': 'วันสุดท้ายของเดือน',
            'yearly': 'รายปี',
        }
        return types[type]

    @api.multi
    def amount_text(self, amount):
        return num2words(amount, to='currency', lang='th')

    @api.multi
    def remove_menu_print(self, res, reports):
        for report in reports:
            reports = self.env.ref(report, raise_if_not_found=False)
            for rec in res.get('toolbar', {}).get('print', []):
                if rec.get('id', False) in reports.ids:
                    del res['toolbar']['print'][
                        res.get('toolbar', {}).get('print').index(rec)]
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        hide_reports_base = [
            'agreement_legal.partner_agreement_contract_document',
            'agreement_legal.partner_agreement_contract_document_preview',
        ]
        is_template = self._context.get('is_template')
        res = super(Agreement, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if res and view_type in ['tree', 'form']:
            # del menu print from template
            if is_template:
                self.remove_menu_print(res, hide_reports_base)
        return res

    def active_statusbar(self):
        if not self.line_ids:
            raise UserError(_('Please add Products/Services.'))
        self.write({
            'state': 'active',
        })
        for rec in self.child_agreements_ids:
            rec.write({
                'state': 'active',
            })

    def inactive_statusbar(self):
        self.write({
            'state': 'inactive',
        })
        for rec in self.child_agreements_ids:
            rec.write({
                'state': 'inactive',
            })

    @api.multi
    def search_contract(self):
        self.ensure_one()
        Contract = self.env['account.analytic.account']
        contracts = Contract.search([('agreement_id', '=', self.id)])
        return contracts

    @api.multi
    def _compute_is_contract_create(self):
        for agreement in self:
            if agreement.search_contract():
                agreement.is_contract_create = True

    @api.multi
    def get_agreement_vals(self):
        self.ensure_one()
        context = self._context.copy()
        return {
            'name': 'NEW',
            'active': True,
            'version': 1,
            'revision': 0,
            'state': 'draft',
            'partner_id': context['partner_id'],
            'partner_contact_id': context['partner_contact_id'],
            'date_contract': context['date_contract'],
            'start_date': context['start_date'],
            'end_date': context['end_date'],
            'recurring_interval': context['recurring_interval'],
            'recurring_rule_type': context['recurring_rule_type'],
            'parent_agreement_id': False,
        }

    @api.multi
    def _create_agreement(self):
        self.ensure_one()
        vals = self.get_agreement_vals()
        # Create agreement
        vals['name'] = '%s - %s' % (self.name, self._context.get('name'))
        vals['extension_agreement_id'] = False
        vals['transfer_agreement_id'] = False
        if self._context.get('extension') is True:
            vals['extension_agreement_id'] = self.id
        if self._context.get('transfer') is True:
            vals['transfer_agreement_id'] = self.id
        new_agreement = self.copy(default=vals)
        if self.line_ids:
            for line in self.line_ids:
                new_agreement.line_ids += line.copy()
        new_agreement.sections_ids.mapped('clauses_ids').write({
            'agreement_id': new_agreement.id})
        # Create child agreement
        vals['parent_agreement_id'] = new_agreement.id
        for child in self.child_agreements_ids:
            vals['name'] = '%s - %s' % (child.name, self._context.get('name'))
            if self._context.get('extension') is True:
                vals['extension_agreement_id'] = child.id
            if self._context.get('transfer') is True:
                vals['transfer_agreement_id'] = child.id
            child_agreement = child.copy(default=vals)
            if child.line_ids:
                for line in self.line_ids:
                    child_agreement.line_ids += line.copy()
            child_agreement.sections_ids.mapped('clauses_ids').write({
                'agreement_id': child_agreement.id})
        return {
            'res_model': 'agreement',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_agreement.id,
        }

    @api.multi
    def action_view_contract(self):
        self.ensure_one()
        if not self.is_contract_create:
            raise UserError(_('Please create contract.'))
        action_id = 'contract.action_account_analytic_%s_overdue_all' \
            % (self.contract_type, )
        action = self.env.ref(action_id).read()[0]
        contracts = self.search_contract()
        if contracts:
            view_id = 'contract.account_analytic_account_%s_form' \
                % (self.contract_type, )
            action.update({
                'views': [(self.env.ref(view_id).id, 'form')],
                'res_id': contracts[0].id,
            })
        return action

    @api.multi
    def prepare_contract(self):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id),
             ], limit=1, )
        return {
            'name': self.name,
            'contract_type': self.contract_type,
            'agreement_id': self.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id,
            'recurring_invoices': True,
            'recurring_interval': self.recurring_interval,
            'recurring_rule_type': self.recurring_rule_type,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'recurring_next_date': self.start_date,
            'parent_contract_id': self._context.get('parent_contract_id'),
            'active': True,
        }

    @api.multi
    def create_new_contract(self):
        self.ensure_one()
        if self.is_contract_create:
            raise UserError(_('Contract is still active.'))
        val = self.prepare_contract()
        contract = self.env['account.analytic.account'].create(val)
        vals = []
        for line in self.line_ids:
            new_line = line.prepare_contract_line()
            vals.append((0, 0, new_line))
        contract.write({'recurring_invoice_line_ids': vals})
        # Create Child Contract
        for child in self.child_agreements_ids:
            child.with_context({'parent_contract_id': contract.id}).\
                create_new_contract()
        return contract
