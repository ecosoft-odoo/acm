# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.queue_job.job import job


class CreateNewYearProduct(models.Model):
    _name = 'create.new.year.product'
    _description = 'Create New Year Product'
    _order = 'name desc'

    name = fields.Selection(
        selection=lambda self: self._get_selection_next_year(),
        string='Next Year',
        required=True,
    )
    product_ids = fields.Many2many(
        comodel_name='product.template',
    )
    product_count = fields.Integer(
        compute='_compute_product_count',
        string='Product Count',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        default='draft',
    )
    job_ids = fields.Many2many(
        comodel_name='queue.job',
        compute='_compute_job',
        help="List all jobs related to this document",
    )
    job_count = fields.Integer(
        string='Job Count',
        compute='_compute_job',
    )
    is_confirmed_on_background = fields.Boolean(
        string='Is Confirmed On Background',
        default=False,
    )

    @api.model
    def _get_selection_next_year(self):
        year_selection = [(str(year), str(year)) for year in range(2020, 2060)]
        return year_selection

    @api.model
    def default_get(self, fields):
        # Lastest version must same year
        products = self.env['product.template'].search([('value_type', '=', 'rent'), ('is_lastest_version', '=', True)])
        year_list = list(set(products.mapped('year')))
        if len(year_list) > 1:
            raise UserError(_('Please check lastest version of all rent product must same year.'))
        # Next year must not created
        next_year = str(int(year_list[0]) + 1)
        create_new_year_products = self.search([('state', 'in', ['draft', 'done']), ('name', '=', next_year)])
        if create_new_year_products:
            raise UserError(_('Next year {} is created already.').format(next_year))
        res = super(CreateNewYearProduct, self).default_get(fields)
        res['name'] = next_year
        return res

    @api.multi
    @api.depends('product_ids')
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    @api.multi
    def _compute_job(self):
        for rec in self:
            rec.job_ids = self.sudo().env['queue.job'].search(
                [('func_string', 'like', 'create.new.year.product({},)'.format(rec.id, ))],
                order='id desc')
            rec.job_count = len(rec.job_ids)

    @api.multi
    @job(default_channel='root')
    def action_create_all_product(self):
        self.ensure_one()
        products = self.env['product.template'].search([('value_type', '=', 'rent'), ('is_lastest_version', '=', True)])
        year_list = list(set(products.mapped('year')))
        if len(year_list) > 1:
            raise UserError(_('Please check lastest version of all rent product must same year.'))
        action = self.env['create.new.version.product'].with_context({
            'active_ids': products.ids, 'next_year': self.name
        }).action_create_new_version()
        product_ids = action['domain'][0][2]
        self.product_ids = self.env['product.template'].browse(product_ids)
        self.write({'state': 'done'})
        return True

    @api.multi
    def action_create_all_product_async(self):
        self.ensure_one()
        if not self.env.context.get('job_uuid') and not self.env.context.get(
            'test_queue_job_no_delay'
        ):
            self.write({'is_confirmed_on_background': True})
            description = _('Creating jobs to create all rent product in year {}').format(self.name)
            new_delay = self.with_delay(description=description).action_create_all_product()
            return 'Job created with uuid {}'.format(new_delay.uuid)
        return super(CreateNewYearProduct, self).action_create_all_product()

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_view_product(self):
        products = self.mapped('product_ids')
        # View Product
        action = self.env.ref('product.product_template_action').read()[0]
        action.update({
            'domain': [('id', 'in', products.ids)],
        })
        if len(products) == 1:
            action.update({
                'views': [(self.env.ref('product.product_template_only_form_view').id, 'form')],
                'res_id': products.id
            })
        return action

    @api.multi
    def action_view_job(self):
        jobs = self.mapped('job_ids')
        # View Job
        action = self.env.ref('queue_job.action_queue_job').read()[0]
        action.update({
            'domain': [('id', 'in', jobs.ids)],
            'context': {},
        })
        if len(jobs) == 1:
            action.update({
                'views': [(self.env.ref('queue_job.view_queue_job_form').id, 'form')],
                'res_id': jobs.id
            })
        return action
