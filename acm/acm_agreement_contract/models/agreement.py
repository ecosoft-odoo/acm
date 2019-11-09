# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from lxml import etree
from num2words import num2words
from dateutil.relativedelta import relativedelta


class Agreement(models.Model):
    _inherit = 'agreement'

    template_id = fields.Many2one(
        comodel_name='agreement',
        string='Template',
    )
    is_extension = fields.Boolean(
        string='Extension',
    )
    extension_agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Source Agreement',
    )
    is_transfer = fields.Boolean(
        string='Transfer',
    )
    transfer_agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Source Agreement',
    )
    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer Contract'),
            ('purchase', 'Supplier Contract'), ],
        default='sale',
        required=True,
    )
    date_contract = fields.Date(
        string='Contract Date',
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
    is_breach = fields.Boolean(
        string='Breach',
    )
    is_termination = fields.Boolean(
        string='Termination',
    )
    reason_termination = fields.Text(
        string='Termination Reason',
    )
    is_contract_create = fields.Boolean(
        compute='_compute_is_contract_create',
    )
    rent_line_id = fields.Many2one(
        comodel_name='agreement.line',
        compute='_compute_line_id',
    )
    tea_money_line_id = fields.Many2one(
        comodel_name='agreement.line',
        compute='_compute_line_id',
    )
    security_deposit_line_id = fields.Many2one(
        comodel_name='agreement.line',
        compute='_compute_line_id',
    )
    transfer_line_id = fields.Many2one(
        comodel_name='agreement.line',
        compute='_compute_line_id',
    )
    breach_ids = fields.One2many(
        comodel_name='agreement.breach',
        inverse_name='agreement_id',
        string='Breach',
    )
    termination_by = fields.Selection(
        selection=[
            ('lessee', 'Lessee'),
            ('lessor', 'Lessor'), ],
        string='Termination By',
    )
    payment_due_date = fields.Integer(
        string='Payment Due Date',
        default=1,
    )

    @api.constrains('start_date', 'end_date')
    @api.multi
    def _check_start_end_date(self):
        self.ensure_one()
        if self.start_date > self.end_date:
            raise UserError(_('"Start Date" cannot be more than "End Date"'))

    @api.multi
    def search_contract(self):
        self.ensure_one()
        Contract = self.env['account.analytic.account']
        contracts = Contract.search([('agreement_id', '=', self.id)])
        return contracts

    @api.multi
    def _compute_is_contract_create(self):
        for rec in self:
            if rec.search_contract():
                rec.is_contract_create = True

    @api.multi
    @api.depends('line_ids')
    def _compute_line_id(self):
        for rec in self:
            lines = rec.line_ids
            if not lines:
                continue
            rent_line_ids = lines.filtered(
                lambda l: l.product_id.value_type == 'rent')
            tea_money_line_ids = lines.filtered(
                lambda l: l.product_id.value_type == 'tea_money')
            security_deposit_line_ids = lines.filtered(
                lambda l: l.product_id.value_type == 'security_deposit')
            transfer_line_ids = lines.filtered(
                lambda l: l.product_id.value_type == 'transfer')
            if rent_line_ids:
                rec.rent_line_id = rent_line_ids[0]
            if tea_money_line_ids:
                rec.tea_money_line_id = tea_money_line_ids[0]
            if security_deposit_line_ids:
                rec.security_deposit_line_id = security_deposit_line_ids[0]
            if transfer_line_ids:
                rec.transfer_line_id = transfer_line_ids[0]

    @api.multi
    def active_statusbar(self):
        for rec in self:
            # Agreement must have product / services
            if not (rec.is_template or rec.line_ids):
                raise UserError(_('Please add Products/Services.'))
            rec.write({
                'state': 'active',
            })

    @api.multi
    def inactive_statusbar(self):
        for rec in self:
            rec.write({
                'state': 'inactive',
            })

    @api.multi
    def get_agreement_vals(self):
        self.ensure_one()
        context = self._context.copy()
        return {
            'name': not context.get('post_name') and self.name or
            '%s - %s' % (self.name, context.get('post_name')),
            'active': True,
            'version': 1,
            'revision': 0,
            'state': 'draft',
            'parent_agreement_id': False,
            'stage_id': self.env.ref('agreement_legal.agreement_stage_new').id,
            'template_id': self.is_template and self.id or self.template_id.id,
            'partner_id': context.get('partner_id'),
            'partner_contact_id': context.get('partner_contact_id'),
            'date_contract': context.get('date_contract'),
            'start_date': context.get('date_start'),
            'end_date': context.get('date_end'),
            'recurring_interval':
                context.get('recurring_interval') or self.recurring_interval,
            'recurring_rule_type':
                context.get('recurring_rule_type') or self.recurring_rule_type,
            'is_extension': context.get('is_extension'),
            'extension_agreement_id': context.get('extension_agreement_id'),
            'is_transfer': context.get('is_transfer'),
            'transfer_agreement_id': context.get('transfer_agreement_id'),
        }

    @api.multi
    def view_agreement(self):
        res = {
            'name': _('Agreements'),
            'res_model': 'agreement',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.ids)],
            'context': {'res_ids': self.ids, },
        }
        if len(self) == 1:
            res.update({'view_mode': 'form', 'res_id': self.id, })
        return res

    @api.multi
    def create_agreement(self):
        if not self:
            raise UserError(_('No Agreement.'))
        agreement_ids = []
        for rec in self:
            vals = rec.get_agreement_vals()
            agreement = rec.copy(default=vals)
            agreement.sections_ids.mapped('clauses_ids').write({
                'agreement_id': agreement.id})
            for line in rec.line_ids:
                agreement.line_ids += line.copy()
            # Update revision
            if agreement.revision:
                self._cr.execute("""
                    update agreement set revision = 0 where id = %s
                """, (agreement.id, ))
            agreement_ids.append(agreement.id)
        new_agreements = self.browse(agreement_ids)
        return new_agreements

    @api.multi
    def prepare_contract(self):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id), ], limit=1, )
        return {
            'code': self.code,
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
            'recurring_next_date':
                self.recurring_rule_type == 'monthly' and
                '%s-%s-%s' % (self.start_date.year, self.start_date.month,
                              self.payment_due_date) or self.start_date,
            'active': True,
        }

    @api.multi
    def create_new_contract(self):
        self.ensure_one()
        if self.is_contract_create:
            raise UserError(_('Contract is still active.'))
        contract_dict = self.prepare_contract()
        contract = self.env['account.analytic.account'].create(contract_dict)
        lines = []
        for line in self.line_ids:
            lines.append((0, 0, line.prepare_contract_line()))
        contract.write({'recurring_invoice_line_ids': lines})
        return True

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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(Agreement, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if not self._context.get('default_is_template', False):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            res['arch'] = etree.tostring(root)
        return res

    @api.model
    def create(self, vals):
        if self._context.get('default_is_template', False):
            vals['code'] = 'Template'
        return super(Agreement, self).create(vals)

    @api.model
    def trans_recurring(self, type):
        types = {
            'daily': 'รายวัน',
            'weekly': 'รายสัปดาห์',
            'monthly': 'รายเดือน',
            'monthlylastday': 'วันสุดท้ายของเดือน',
            'yearly': 'รายปี',
        }
        return types[type]

    @api.model
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

    @api.model
    def amount_text(self, amount):
        return num2words(amount, to='currency', lang='th')

    @api.multi
    def get_rent_text(self):
        self.ensure_one()
        rent_lines = self.line_ids.filtered(
            lambda l: l.product_id.value_type == 'rent').sorted('date_start')
        if len(rent_lines) <= 1:
            return ' %s บาท (%s)' % (
                '{0:,.0f}'.format(rent_lines.lst_price),
                self.amount_text(rent_lines.lst_price))
        else:
            rent_text = ''
            for index, rent_line in enumerate(rent_lines):
                rent_text += ' ปีที่ %s %s บาท (%s)' % (
                    str(index+1), '{0:,.0f}'.format(rent_line.lst_price),
                    self.amount_text(rent_line.lst_price))
            return rent_text

    @api.multi
    def _compute_line_start_end_date(self, rental_number):
        for line in self.mapped('line_ids'):
            date_valid = False
            start_date = line.agreement_id.start_date
            end_date = line.agreement_id.end_date
            if line.date_start:
                line.date_start += relativedelta(years=rental_number)
                date_valid = start_date <= line.date_start <= end_date
            if line.date_end:
                line.date_end += relativedelta(years=rental_number)
                date_valid = start_date <= line.date_end <= end_date
            if not date_valid:
                raise UserError(
                    _('Date in Products/Services is not valid.'))
