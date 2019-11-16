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
        string='Source Agreement (Extension)',
    )
    is_transfer = fields.Boolean(
        string='Transfer',
    )
    transfer_agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Source Agreement (Transfer)',
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
    rent_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        string='Product',
        store=True,
    )
    lump_sum_rent_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        store=True,
    )
    security_deposit_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        store=True,
    )
    transfer_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        store=True,
    )
    breach_ids = fields.One2many(
        comodel_name='agreement.breach.line',
        inverse_name='agreement_id',
        string='Breach Lines',
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
    partner_id = fields.Many2one(
        string='Lessee',
    )
    partner_contact_id = fields.Many2one(
        string='Lessee Contact',
    )
    partner_contact_phone = fields.Char(
        string='Lessee Phone',
    )
    partner_contact_email = fields.Char(
        string='Lessee Email',
    )
    partner_signed_date = fields.Date(
        string='Signed on (Lessee)',
    )
    partner_signed_user_id = fields.Many2one(
        string='Signed By (Lessee)',
    )
    company_id = fields.Many2one(
        string='Lessor',
    )
    company_contact_id = fields.Many2one(
        string='Lessor Contact',
    )
    company_contact_phone = fields.Char(
        string='Lessor Phone',
    )
    company_contact_email = fields.Char(
        string='Lessor Email',
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='rent_product_id.group_id',
        string='Zone',
        store=True,
    )
    product_category_id = fields.Many2one(
        related='rent_product_id.goods_category_id',
        string='Product Category',
    )
    product_number = fields.Char(
        related='rent_product_id.lock_number',
        string='Lock',
    )
    state = fields.Selection(
        string='Status',
    )

    @api.constrains('start_date', 'end_date')
    @api.multi
    def _check_start_end_date(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise UserError(
                    _('"Start Date" cannot be more than "End Date"'))

    @api.constrains('rent_product_id', 'state')
    def _check_rent_product_id(self):
        for rec in self:
            if rec.state == 'active':
                # No rent product
                if not rec.rent_product_id:
                    raise UserError(_('Please add rental product.'))
                # No multiple rent product
                agreements = self.env['agreement'].search(
                    [('state', '=', 'active'),
                     ('rent_product_id', '=', rec.rent_product_id.id), ],
                    order='id')
                if len(agreements) > 1:
                    raise UserError(_(
                        'The rental product is duplicated with %s.'
                        % (agreements[0].name, )))

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for rec in self:
            lines = rec.line_ids
            rent_products = \
                lines.filtered(lambda l: l.product_id.value_type == 'rent') \
                .mapped('product_id')
            if len(rent_products) > 1:
                raise UserError(_('Only one rental product is allowed.'))

    @api.multi
    def search_contract(self):
        Contract = self.env['account.analytic.account']
        contracts = Contract.search([('agreement_id', 'in', self.ids)])
        return contracts

    @api.multi
    def _compute_is_contract_create(self):
        for rec in self:
            if rec.search_contract():
                rec.is_contract_create = True

    @api.depends('line_ids', 'line_ids.product_id')
    @api.multi
    def _compute_product_id(self):
        for rec in self:
            lines = rec.line_ids
            rent_product = lines.filtered(
                lambda l: l.product_id.value_type == 'rent') \
                .mapped('product_id')
            lump_sum_rent_product = lines.filtered(
                lambda l: l.product_id.value_type == 'lump_sum_rent') \
                .mapped('product_id')
            security_deposit_product = lines.filtered(
                lambda l: l.product_id.value_type == 'security_deposit') \
                .mapped('product_id')
            transfer_product = lines.filtered(
                lambda l: l.product_id.value_type == 'transfer') \
                .mapped('product_id')
            if rent_product:
                rec.rent_product_id = rent_product[0]
            if lump_sum_rent_product:
                rec.lump_sum_rent_product_id = lump_sum_rent_product[0]
            if security_deposit_product:
                rec.security_deposit_product_id = security_deposit_product[0]
            if transfer_product:
                rec.transfer_product_id = transfer_product[0]

    @api.model
    def _validate_rent_product_dates(self, product_lines):
        sorted_lines = product_lines.filtered(
            lambda l: l.product_id and
            l.product_id.value_type == 'rent').sorted('date_start')
        count = len(sorted_lines)
        err = False
        for i in range(count):
            if i == 0:  # Check first date
                err = self.start_date != sorted_lines[i].date_start
            if not err and i == count-1:  # Check last date
                err = self.end_date != sorted_lines[i].date_end
            if not err and i < count-1:
                next_date = sorted_lines[i].date_end + relativedelta(days=1)
                err = next_date != sorted_lines[i+1].date_start
            if err:
                raise UserError(_("Rental product's start/end dates "
                                  "not in continuing sequence"))

    @api.multi
    def active_statusbar(self):
        for rec in self:
            # Agreement must have product / services
            if not (rec.is_template or rec.line_ids):
                raise UserError(_('Please add Products/Services.'))
            # Validate rent product dates sequence
            self._validate_rent_product_dates(rec.line_ids)
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
            'group_id': self.group_id.id,
        }

    @api.multi
    def create_new_contract(self):
        Contract = self.env['account.analytic.account']
        contracts = Contract
        for rec in self:
            if rec.state != 'active':
                raise UserError(_('State %s is not active.') % (rec.name, ))
            if rec.is_contract_create:
                raise UserError(_('Contract %s is still active.')
                                % (rec.name, ))
            contract_dict = rec.prepare_contract()
            contract = Contract.create(contract_dict)
            lines = []
            for line in rec.line_ids:
                lines.append((0, 0, line.prepare_contract_line()))
            contract.write({'recurring_invoice_line_ids': lines})
            contracts |= contract
        return contracts

    @api.multi
    def action_view_contract(self):
        if not self:
            raise UserError(_('Please select agreement.'))
        if len(list(set(self.mapped('contract_type')))) > 1:
            raise UserError(_('Not multiple contract type.'))
        action_id = 'contract.action_account_analytic_%s_overdue_all' \
            % (self[0].contract_type, )
        action = self.env.ref(action_id).read()[0]
        contracts = self.search_contract()
        if len(contracts) == 1:
            view_id = 'contract.account_analytic_account_%s_form' \
                % (self[0].contract_type, )
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
                '{0:,.2f}'.format(rent_lines.lst_price),
                self.amount_text(rent_lines.lst_price))
        else:
            rent_text = ''
            for index, rent_line in enumerate(rent_lines):
                rent_text += ' ปีที่ %s %s บาท (%s)' % (
                    str(index+1), '{0:,.2f}'.format(rent_line.lst_price),
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
            if (line.date_start or line.date_end) and not date_valid:
                raise UserError(
                    _('Date in Products/Services is not valid.'))

    @api.multi
    def filter_lines(self, value_type=''):
        return self.line_ids.filtered(
            lambda l: l.product_id.value_type == value_type)
