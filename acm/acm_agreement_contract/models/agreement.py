# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from lxml import etree
from num2words import num2words
from collections import namedtuple
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import datetime


class Agreement(models.Model):
    _inherit = 'agreement'

    # Normal Field
    template_id = fields.Many2one(
        comodel_name='agreement',
        string='Template',
        states={'active': [('readonly', True)]},
    )
    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer Contract'),
            ('purchase', 'Supplier Contract'), ],
        default='sale',
        required=True,
        states={'active': [('readonly', True)]},
    )
    date_contract = fields.Date(
        string='Contract Date',
        states={'active': [('readonly', True)]},
    )
    recurring_interval = fields.Integer(
        string='Repeat Every',
        help='Repeat every (Days/Week/Month/Year)',
        default=1,
        states={'active': [('readonly', True)]},
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
        default='monthly',
        states={'active': [('readonly', True)]},
    )
    is_contract_create = fields.Boolean(
        compute='_compute_is_contract_create',
    )
    contract_count = fields.Integer(
        compute='_compute_contract_count',
    )
    rent_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        string='Rental Product',
        store=True,
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='rent_product_id.group_id',
        string='Zone',
        store=True,
    )
    subzone = fields.Char(
        related='rent_product_id.subzone',
        string='Subzone',
    )
    partner_id = fields.Many2one(
        string='Lessee',
        states={'active': [('readonly', True)]},
    )
    partner_contact_id = fields.Many2one(
        string='Lessee Contact',
        states={'active': [('readonly', True)]},
    )
    partner_contact_phone = fields.Char(
        string='Lessee Phone',
    )
    partner_contact_email = fields.Char(
        string='Lessee Email',
    )
    partner_signed_date = fields.Date(
        string='Signed on (Lessee)',
        states={'active': [('readonly', True)]},
    )
    partner_signed_user_id = fields.Many2one(
        string='Signed By (Lessee)',
        states={'active': [('readonly', True)]},
    )
    company_id = fields.Many2one(
        string='Lessor',
        states={'active': [('readonly', True)]},
    )
    company_contact_id = fields.Many2one(
        string='Lessor Contact',
        default=lambda self: self._default_company_contract_id(),
        states={'active': [('readonly', True)]},
    )
    company_contact_phone = fields.Char(
        string='Lessor Phone',
    )
    company_contact_email = fields.Char(
        string='Lessor Email',
    )
    state = fields.Selection(
        string='Status',
    )
    expiry_time = fields.Char(
        string='Time to Expiry (Months)',
        compute='_compute_expiry_time',
    )
    inactive_reason = fields.Selection(
        selection=[
            ('cancel', 'Cancelled'),
            ('terminate', 'Terminated'),
            ('transfer', 'Transferred'),
            ('expire', 'Expired'),
        ],
        string='Inactive Reason',
    )
    is_transfer = fields.Boolean(
        string='Is transfer ?',
        copy=False,
    )
    is_terminate = fields.Boolean(
        string='Is terminate ?',
        copy=False,
    )
    # Set field readonly = True for state is active.
    name = fields.Char(
        states={'active': [('readonly', True)]},
    )
    is_template = fields.Boolean(
        states={'active': [('readonly', True)]},
    )
    version = fields.Integer(
        states={'active': [('readonly', True)]},
    )
    revision = fields.Integer(
        states={'active': [('readonly', True)]},
    )
    description = fields.Text(
        states={'active': [('readonly', True)]},
    )
    start_date = fields.Date(
        states={'active': [('readonly', True)]},
    )
    end_date = fields.Date(
        states={'active': [('readonly', True)]},
    )
    color = fields.Integer(
        states={'active': [('readonly', True)]},
    )
    active = fields.Boolean(
        states={'active': [('readonly', True)]},
    )
    company_signed_date = fields.Date(
        states={'active': [('readonly', True)]},
    )
    term = fields.Integer(
        states={'active': [('readonly', True)]},
    )
    expiration_notice = fields.Integer(
        states={'active': [('readonly', True)]},
    )
    change_notice = fields.Integer(
        states={'active': [('readonly', True)]},
    )
    special_terms = fields.Text(
        states={'active': [('readonly', True)]},
    )
    code = fields.Char(
        states={'active': [('readonly', True)]},
    )
    increase_type_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    termination_date = fields.Date(
        states={'active': [('readonly', True)]},
        copy=False,
    )
    reviewed_date = fields.Date(
        states={'active': [('readonly', True)]},
    )
    reviewed_user_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    approved_date = fields.Date(
        states={'active': [('readonly', True)]},
    )
    approved_user_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    currency_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    use_parties_content = fields.Boolean(
        states={'active': [('readonly', True)]},
    )
    parties = fields.Html(
        states={'active': [('readonly', True)]},
    )
    agreement_type_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    agreement_subtype_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    product_ids = fields.Many2many(
        states={'active': [('readonly', True)]},
    )
    assigned_user_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    company_signed_user_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    parent_agreement_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    renewal_type_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    recital_ids = fields.One2many(
        states={'active': [('readonly', True)]},
    )
    sections_ids = fields.One2many(
        states={'active': [('readonly', True)]},
    )
    clauses_ids = fields.One2many(
        states={'active': [('readonly', True)]},
    )
    previous_version_agreements_ids = fields.One2many(
        states={'active': [('readonly', True)]},
    )
    child_agreements_ids = fields.One2many(
        states={'active': [('readonly', True)]},
    )
    line_ids = fields.One2many(
        states={'active': [('readonly', True)]},
    )
    notification_address_id = fields.Many2one(
        states={'active': [('readonly', True)]},
    )
    signed_contract_filename = fields.Char(
        states={'active': [('readonly', True)]},
    )
    signed_contract = fields.Binary(
        states={'active': [('readonly', True)]},
    )
    field_domain = fields.Char(
        states={'active': [('readonly', True)]},
    )
    default_value = fields.Char(
        states={'active': [('readonly', True)]},
    )
    copyvalue = fields.Char(
        states={'active': [('readonly', True)]},
    )
    # Breach Agreement
    is_breach = fields.Boolean(
        string='Breach',
        states={'active': [('readonly', True)]},
    )
    breach_line_ids = fields.One2many(
        comodel_name='agreement.breach.line',
        inverse_name='agreement_id',
        string='Breach Lines',
        states={'active': [('readonly', True)]},
    )
    # Termination Agreement
    reason_termination = fields.Text(
        string='Termination Reason',
        states={'active': [('readonly', True)]},
        copy=False,
    )
    termination_by = fields.Selection(
        selection=[
            ('lessee', 'Lessee'),
            ('lessor', 'Lessor'), ],
        string='Termination By',
        states={'active': [('readonly', True)]},
        copy=False,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Vendor Bill',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
    )
    invoice_date_days = fields.Integer(
        string='Invoice Date (Days)',
        states={'active': [('readonly', True)]},
        copy=False,
    )
    agreement_invoice_line = fields.One2many(
        comodel_name='agreement.invoice.line',
        inverse_name='agreement_id',
        readonly=True,
        copy=False,
    )
    show_invoice_date = fields.Boolean(
        related='company_id.show_invoice_date',
    )

    @api.model
    def _default_company_contract_id(self):
        company = self.env['res.company']._company_default_get()
        company_contact = self.env['res.partner'].search(
            [('parent_id', '=', company.partner_id.id)])
        if len(company_contact) > 1:
            company_contact = company_contact[0]
        return company_contact

    @api.constrains('start_date', 'end_date')
    def _check_start_end_date(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise UserError(
                    _("Agreement '%s' start date can't be later than end date")
                    % (rec.name, ))

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for rec in self:
            rent_products = \
                rec.line_ids.filtered(
                    lambda l: l.product_id.value_type == 'rent').mapped(
                        'product_id')
            if len(rent_products) > 1:
                raise UserError(_('Only one rental product is allowed.'))

    @api.multi
    def _search_contract(self):
        Contract = self.env['account.analytic.account']
        contracts = Contract.search([('agreement_id', 'in', self.ids)])
        return contracts

    @api.multi
    def _compute_is_contract_create(self):
        for rec in self:
            rec.is_contract_create = rec._search_contract() and True or False

    @api.depends('line_ids')
    def _compute_product_id(self):
        for rec in self:
            rent_products = rec.line_ids.filtered(
                lambda l: l.product_id.value_type == 'rent') \
                .mapped('product_id')
            if rent_products:
                rec.rent_product_id = rent_products[0]

    @api.multi
    def _compute_contract_count(self):
        for rec in self:
            contracts = rec.with_context(active_test=False)._search_contract()
            rec.contract_count = len(contracts)

    @api.multi
    def _compute_expiry_time(self):
        now = fields.Date.today()
        for rec in self:
            expiry_time = '0.00'
            if rec.state == 'active' and rec.end_date and rec.end_date >= now:
                time = relativedelta(rec.end_date, now)
                if rec.start_date > now:
                    time = relativedelta(
                        rec.end_date, rec.start_date - timedelta(1))
                expiry_time = '%s.%s' % (
                    str(time.years * 12 + time.months).zfill(2),
                    str(time.days).zfill(2))
            rec.expiry_time = expiry_time

    @api.multi
    def _validate_active_agreement(self):
        for rec in self:
            # Agreement must be state to draft
            if rec.state != 'draft':
                raise UserError(_("Agreement's state must be draft."))
            # Agreement must have products/services
            if not rec.line_ids:
                raise UserError(_('Please add Products/Services.'))
            # Agreement must have rental product
            if not rec.rent_product_id:
                raise UserError(_('Please add rental product.'))
            # Rental product not duplicated with other agreement in same date
            Range = namedtuple('Range', ['start', 'end'])
            agreements = self.env['agreement'].search(
                [('state', '=', 'active'),
                 ('rent_product_id', '=', rec.rent_product_id.id),
                 # no check for transfer agreement case
                 ('is_transfer', '=', False), ])
            for agreement in agreements:
                r1 = Range(start=agreement.start_date, end=agreement.end_date)
                r2 = Range(start=rec.start_date, end=rec.end_date)
                latest_start = max(r1.start, r2.start)
                earliest_end = min(r1.end, r2.end)
                delta = (earliest_end - latest_start).days + 1
                overlap = max(0, delta)
                if overlap:
                    raise UserError(
                        _('The rental product is duplicated in same period '
                          'with %s' % (agreement.name, )))
        return True

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
    def _validate_contract_create(self):
        for rec in self:
            if rec.state != 'active':
                raise UserError(_('Agreement is not active.'))
            if not rec.is_contract_create:
                raise UserError(_('Contract is not active.'))
        return True

    @api.multi
    def _create_agreement_invoice_line(self):
        for rec in self:
            vals = []
            rec.agreement_invoice_line.unlink()
            # Not create agreement invoice line
            if not rec.show_invoice_date or rec.is_template or \
               rec.recurring_rule_type != 'monthly':
                return
            # Create agreement invoice line
            try:
                if rec.invoice_date_days < rec.start_date.day:
                    date = rec.start_date + relativedelta(months=+1)
                    vals.extend([{
                        'number': 1,
                        'date_invoice': rec.start_date,
                        'agreement_id': rec.id,
                    }, {
                        'number': 2,
                        'date_invoice': '%s-%s-%s' % (
                            date.year, date.month, rec.invoice_date_days
                        ),
                        'agreement_id': rec.id,
                    }])
                else:
                    vals.extend([{
                        'number': 1,
                        'date_invoice': '%s-%s-%s' % (
                            rec.start_date.year, rec.start_date.month,
                            rec.invoice_date_days
                        ),
                        'agreement_id': rec.id,
                    }])
                self.env['agreement.invoice.line'].create(vals)
            except Exception as ex:
                raise UserError(_(ex))

    @api.multi
    def active_statusbar(self):
        for rec in self:
            if not rec.is_template:
                # Validate active agreement
                rec._validate_active_agreement()
                # Validate rent product dates sequence
                rec._validate_rent_product_dates(rec.line_ids)
                # Create agreement invoice line
                rec._create_agreement_invoice_line()
            rec.write({'state': 'active', })

    @api.multi
    def inactive_statusbar(self):
        for rec in self:
            if rec.state == 'inactive':
                raise UserError(_("Agreement's state must not be inactive."))
            contract = rec._search_contract()
            contract.write({'active': False, })
            rec.write({'state': 'inactive', })

    @api.multi
    def get_agreement_vals(self):
        self.ensure_one()
        context = self._context.copy()
        return {
            'name': not context.get('post_name') and self.name or
            '%s %s' % (self.name, context.get('post_name')),
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
        }
        if len(self) == 1:
            res.update({'view_mode': 'form', 'res_id': self.id, })
        return res

    @api.multi
    def create_agreement(self):
        agreement_ids = []
        for rec in self:
            vals = rec.get_agreement_vals()
            agreement = rec.copy(default=vals)
            # Write description
            if agreement.name != agreement.description:
                agreement.description = agreement.name
            agreement.sections_ids.mapped('clauses_ids').write({
                'agreement_id': agreement.id, })
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
    def _prepare_contract(self):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', self.contract_type),
             ('company_id', '=', self.company_id.id), ], limit=1, )
        recurring_next_date = self.start_date
        line = self.agreement_invoice_line.filtered(lambda l: l.number == 1)
        if line:
            recurring_next_date = line.date_invoice
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
            'recurring_next_date': recurring_next_date,
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
            contract_dict = rec._prepare_contract()
            contract = Contract.create(contract_dict)
            lines = []
            for line in rec.line_ids:
                lines.append((0, 0, line._prepare_contract_line()))
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
        contracts = self.with_context(active_test=False)._search_contract()
        action.update({
            'domain': [('id', 'in', contracts.ids)],
            'context': {'active_test': False, },
        })
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
        """
        Replace permission on agreement
        - Every user can not permission to create agreement.
        """
        res = super(Agreement, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self._context.get('default_is_template', False):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            res['arch'] = etree.tostring(root)
        return res

    @api.model
    def create(self, vals):
        """
        Define code on agreement template is 'template'.
        """
        if self._context.get('default_is_template', False):
            vals['code'] = 'Template'
        return super(Agreement, self).create(vals)

    @api.model
    def trans_recurring(self, type):
        """
        Translate recurring rule type.
        """
        types = {
            'daily': 'รายวัน',
            'weekly': 'รายสัปดาห์',
            'monthly': 'รายเดือน',
            'monthlylastday': 'วันสุดท้ายของเดือน',
            'yearly': 'รายปี',
        }
        return types[type]

    @api.model
    def trans_months(self, month, abbreviate=False):
        """
        Translate month
        - abbreviate is True > month's abbreviate name.
        - abbreviate is False > month's full name.
        """
        months = {
            '01': ['มกราคม', 'ม.ค.'],
            '02': ['กุมภาพันธ์', 'ก.พ.'],
            '03': ['มีนาคม', 'มี.ค.'],
            '04': ['เมษายน', 'เม.ย.'],
            '05': ['พฤษภาคม', 'พ.ค.'],
            '06': ['มิถุนายน', 'มิ.ย.'],
            '07': ['กรกฎาคม', 'ก.ค.'],
            '08': ['สิงหาคม', 'ส.ค.'],
            '09': ['กันยายน', 'ก.ย.'],
            '10': ['ตุลาคม', 'ต.ค.'],
            '11': ['พฤศจิกายน', 'พ.ย.'],
            '12': ['ธันวาคม', 'ธ.ค.'],
        }
        return abbreviate and months[month][1] or months[month][0]

    @api.model
    def amount_text(self, amount):
        return num2words(amount, to='currency', lang='th')

    @api.multi
    def filter_lines(self, value_type=''):
        return self.line_ids.filtered(
            lambda l: l.product_id.value_type == value_type)

    @api.multi
    def get_rental_period(self, date_start, date_end):
        rent_period = ''
        if date_start and date_end:
            period = relativedelta(
                date_end, date_start - relativedelta(days=1))
            rent_period += str(period.years) + ' ปี ' + \
                str(period.months) + ' เดือน ' + str(period.days) + ' วัน'
        return rent_period

    @api.multi
    def _compute_line_start_end_date(self, time):
        for line in self.mapped('line_ids'):
            # Manual Lines (Start Date, End Date = Contract Date)
            # e.g., Security Deposit, Lum Sum Rent
            if line.manual:
                line.write({
                    'date_start': line.agreement_id.date_contract,
                    'date_end': line.agreement_id.date_contract,
                })
                continue
            # Not Manual Lines
            # e.g., Rental
            if line.date_start:
                line.date_start += time
            if line.date_end:
                line.date_end += time

    @api.model
    def cron_inactive_statusbar(self):
        today = datetime.datetime.now().date()
        agreements = self.with_context(cron=True).search(
            [('state', '=', 'active'),
             '|', ('is_transfer', '=', True),
             '|', ('is_terminate', '=', True),
             ('end_date', '<', today)])
        for agreement in agreements:
            if agreement.is_transfer and agreement.termination_date < today:
                agreement.inactive_statusbar()
                agreement.inactive_reason = 'transfer'
            elif agreement.is_terminate and agreement.termination_date < today:
                agreement.inactive_statusbar()
                agreement.inactive_reason = 'terminate'
            elif not(agreement.is_transfer or agreement.is_terminate) and \
                    agreement.end_date < today:
                agreement.inactive_statusbar()
                agreement.inactive_reason = 'expire'
        return True


class AgreementLine(models.Model):
    _inherit = 'agreement.line'

    qty = fields.Float(
        default=1,
    )
    lst_price = fields.Float(
        string='Unit Price',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    manual = fields.Boolean(
        string='Manual',
        default=False,
        help="Allow using this line to create manual invoice",
    )

    @api.multi
    def _prepare_contract_line(self):
        return {
            'product_id': self.product_id.id,
            'name': self.name,
            'quantity': self.qty,
            'uom_id': self.uom_id.id,
            'specific_price': self.lst_price,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'manual': self.manual,
        }

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        self.lst_price = self.product_id.lst_price
        if self.product_id.description:
            self.name = self.product_id.description


class AgreementInvoiceLine(models.Model):
    _name = 'agreement.invoice.line'
    _description = 'Agreement Invoice Line'

    number = fields.Integer(
        string='No.',
    )
    date_invoice = fields.Date(
        string='Invoice Date',
    )
    agreement_id = fields.Many2one(
        comodel_name='agreement',
    )
