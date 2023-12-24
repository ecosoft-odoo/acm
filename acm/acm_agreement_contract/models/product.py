# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools import pycompat
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'sequence, is_lastest_version desc, group_id, lock_number, subzone'

    width = fields.Float(
        string='Width',
    )
    length1 = fields.Float(
        string='Length',
    )
    area = fields.Float(
        string='Area For Lease',
        digits=dp.get_precision('Area'),
    )
    working_hours_id = fields.Many2one(
        comodel_name='acm.working.hours',
        string='Working Hours',
        # compute='_compute_working_hours_id',
        # inverse='_set_working_hours_id',
        domain="[('type', '=', 'in_time')]",
        store=True,
    )
    working_hours2_id = fields.Many2one(
        comodel_name='acm.working.hours',
        string='Not Working Hours',
        # compute='_compute_working_hours2_id',
        # inverse='_set_working_hours2_id',
        domain="[('type', '=', 'out_time')]",
        store=True,
    )
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('lump_sum_rent', 'Lump Sum Rent'),
            ('security_deposit', 'Security Deposit'),
            ('transfer', 'Transfer'),
        ],
        string='Value Type',
    )
    # goods_type = fields.Char(
    #     string='Goods Type',
    #     compute='_compute_goods_type',
    #     inverse='_set_goods_type',
    #     store=True,
    # )
    # goods_category_id = fields.Many2one(
    #     comodel_name='goods.category',
    #     string='Goods Category',
    #     compute='_compute_goods_category_id',
    #     inverse='_set_goods_category_id',
    #     store=True,
    # )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
    )
    subzone = fields.Char(
        string='Subzone',
    )
    lock_number = fields.Char(
        string='Number',
    )
    lock_attribute = fields.Many2one(
        comodel_name='lock.attribute',
    )
    manual = fields.Boolean()
    origin_product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Origin Product',
        readonly=True,
        copy=False,
        index=True,
    )
    new_product_template_ids = fields.One2many(
        comodel_name='product.template',
        inverse_name='origin_product_template_id',
        string='New Products',
        copy=False,
        context={'active_test': False},
    )
    product_pricelist_ids = fields.One2many(
        comodel_name='acm.product.pricelist',
        inverse_name='product_template_id',
        string='Product Pricelist',
        copy=False,
        context={'active_test': False},
    )
    year = fields.Selection(
        selection=lambda self: self._get_selection_year(),
        string='Year',
    )
    version = fields.Selection(
        selection=lambda self: self._get_selection_version(),
        string='Version',
    )
    date_start = fields.Date(
        string='Product Start Date',
        compute='_compute_date_start',
        inverse='_set_date_start',
        store=True,
        copy=False,
    )
    date_end = fields.Date(
        string='Product End Date',
        compute='_compute_date_end',
        inverse='_set_date_end',
        store=True,
        copy=False,
    )
    is_lastest_version = fields.Boolean(
        string='Is Lastest Version',
        copy=False,
    )
    not_year_version = fields.Boolean(
        string='Not Year and Version',
        default=False,
        copy=False,
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]

    # @api.depends('product_variant_ids', 'product_variant_ids.goods_type')
    # def _compute_goods_type(self):
    #     unique_variants = self.filtered(
    #         lambda template: len(template.product_variant_ids) == 1)
    #     for template in unique_variants:
    #         template.goods_type = template.product_variant_ids.goods_type
    #     for template in (self - unique_variants):
    #         template.goods_type = ''

    # @api.one
    # def _set_goods_type(self):
    #     if len(self.product_variant_ids) == 1:
    #         self.product_variant_ids.goods_type = self.goods_type

    # @api.depends('product_variant_ids',
    #              'product_variant_ids.goods_category_id')
    # def _compute_goods_category_id(self):
    #     unique_variants = self.filtered(
    #         lambda template: len(template.product_variant_ids) == 1)
    #     for template in unique_variants:
    #         template.goods_category_id = \
    #             template.product_variant_ids.goods_category_id.id
    #     for template in (self - unique_variants):
    #         template.goods_category_id = False

    # @api.one
    # def _set_goods_category_id(self):
    #     if len(self.product_variant_ids) == 1:
    #         self.product_variant_ids.goods_category_id = \
    #             self.goods_category_id.id

    @api.depends('product_variant_ids', 'product_variant_ids.date_start')
    def _compute_date_start(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.date_start = template.product_variant_ids.date_start
        for template in (self - unique_variants):
            template.date_start = False

    @api.one
    def _set_date_start(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.date_start = self.date_start

    @api.depends('product_variant_ids', 'product_variant_ids.date_end')
    def _compute_date_end(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.date_end = template.product_variant_ids.date_end
        for template in (self - unique_variants):
            template.date_end = False

    @api.one
    def _set_date_end(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.date_end = self.date_end

    @api.constrains('date_start', 'year')
    def _check_date_start_year(self):
        for rec in self:
            if rec.date_start and str(rec.date_start.year) != rec.year:
                raise UserError(_('Product start date must be in year {}.').format(rec.year))

    @api.constrains('date_start', 'date_end')
    def _check_date_start_date_end(self):
        for rec in self:
            if rec.date_end and not rec.date_start:
                raise UserError(_('Do not update product end date if product start date is not defined.'))
            if rec.date_end and rec.date_start and rec.date_end < rec.date_start:
                raise UserError(_('Product end date must greater than or equal to product start date.'))

    @api.model
    def _get_selection_year(self):
        year_selection = [(str(year), str(year)) for year in range(2020, 2060)]
        return year_selection

    @api.model
    def _get_selection_version(self):
        version_selection = [(str(i).zfill(4), str(i).zfill(4)) for i in range(1, 10)]
        return version_selection

    @api.constrains('value_type')
    def _check_value_type(self):
        # If have pricelist, new product, value type must be rent only
        for rec in self:
            if rec.value_type != 'rent' and (rec.new_product_template_ids or rec.product_pricelist_ids):
                raise UserError(_('Do not change value type because a new product or pricelist not empty.'))

    # @api.depends('product_variant_ids',
    #              'product_variant_ids.working_hours_id')
    # def _compute_working_hours_id(self):
    #     unique_variants = self.filtered(
    #         lambda template: len(template.product_variant_ids) == 1)
    #     for template in unique_variants:
    #         template.working_hours_id = \
    #             template.product_variant_ids.working_hours_id.id
    #     for template in (self - unique_variants):
    #         template.working_hours_id = False

    # @api.one
    # def _set_working_hours_id(self):
    #     if len(self.product_variant_ids) == 1:
    #         self.product_variant_ids.working_hours_id = \
    #             self.working_hours_id.id

    # @api.depends('product_variant_ids',
    #              'product_variant_ids.working_hours2_id')
    # def _compute_working_hours2_id(self):
    #     unique_variants = self.filtered(
    #         lambda template: len(template.product_variant_ids) == 1)
    #     for template in unique_variants:
    #         template.working_hours2_id = \
    #             template.product_variant_ids.working_hours2_id.id
    #     for template in (self - unique_variants):
    #         template.working_hours2_id = False

    # @api.one
    # def _set_working_hours2_id(self):
    #     if len(self.product_variant_ids) == 1:
    #         self.product_variant_ids.working_hours2_id = \
    #             self.working_hours2_id.id

    @api.onchange('year', 'version', 'group_id', 'subzone', 'lock_number')
    def _onchange_year_version_group_subzone_lock_number(self):
        """
            If product type is rent, format name should be YEAR-VERSION-GROUP-SUBZONE-LOCK_NUMBER
            Ex: 2023-0001-1A-001 or 2023-0001-1F-T-001
        """
        names = []
        if self.year:
            names.append(self.year)
        if self.version:
            names.append(self.version)
        if self.group_id:
            names.append(self.group_id.name)
        if self.subzone:
            names.append(self.subzone)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '-'.join(names)

    @api.onchange('manual')
    def _onchange_manual(self):
        """ If select manual field, let reset width, length and area """
        self.width = 0
        self.length1 = 0
        self.area = 0

    @api.onchange('width', 'length1')
    def _onchange_width_length(self):
        """ Area = Width x Length """
        self.area = self.width * self.length1

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(ProductTemplate, self).create(vals_list)
        for template, vals in pycompat.izip(templates, vals_list):
            related_vals = {}
    #         if vals.get('working_hours_id'):
    #             related_vals['working_hours_id'] = vals['working_hours_id']
    #         if vals.get('working_hours2_id'):
    #             related_vals['working_hours2_id'] = vals['working_hours2_id']
    #         if vals.get('goods_type'):
    #             related_vals['goods_type'] = vals['goods_type']
    #         if vals.get('goods_category_id'):
    #             related_vals['goods_category_id'] = vals['goods_category_id']
            if vals.get('date_start'):
                related_vals['date_start'] = vals['date_start']
            if vals.get('date_end'):
                related_vals['date_end'] = vals['date_end']
            if related_vals:
                template.write(related_vals)
        return templates

    @api.multi
    def action_view_product(self):
        new_products = self.mapped('new_product_template_ids')
        # View Product
        action = self.env.ref('product.product_template_action').read()[0]
        action.update({
            'domain': [('id', 'in', new_products.ids)],
        })
        if len(new_products) == 1:
            action.update({
                'views': [(self.env.ref('product.product_template_only_form_view').id, 'form')],
                'res_id': new_products.id
            })
        return action

    @api.multi
    def _update_sequence(self):
        self.ensure_one()
        if self.value_type == 'rent':
            sequence = 1
        elif self.value_type == 'lump_sum_rent':
            sequence = 2
        elif self.value_type == 'security_deposit':
            sequence = 3
        elif self.value_type == 'transfer':
            sequence = 4
        else:
            sequence = 999
        if sequence != self.sequence:
            self.write({'sequence': sequence})

    @api.model
    def create(self, vals):
        product = super(ProductTemplate, self).create(vals)
        # Update sequence
        product._update_sequence()
        return product

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for product in self:
            # Update active field on product pricelist
            if 'active' in vals:
                product.product_pricelist_ids.write({'active': vals['active']})
            # Update sequence
            product._update_sequence()
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'sequence, is_lastest_version desc, group_id, lock_number, subzone'

    # goods_type = fields.Char(
    #     string='Goods Type',
    # )
    # goods_category_id = fields.Many2one(
    #     comodel_name='goods.category',
    #     string='Goods Category',
    # )
    # working_hours_id = fields.Many2one(
    #     comodel_name='acm.working.hours',
    #     string='Working Hours',
    #     domain="[('type', '=', 'in_time')]",
    # )
    # working_hours2_id = fields.Many2one(
    #     comodel_name='acm.working.hours',
    #     string='Not Working Hours',
    #     domain="[('type', '=', 'out_time')]",
    # )
    date_start = fields.Date(
        string='Product Start Date',
        copy=False,
    )
    date_end = fields.Date(
        string='Product End Date',
        copy=False,
    )

    @api.onchange('year', 'version', 'group_id', 'subzone', 'lock_number')
    def _onchange_year_version_group_subzone_lock_number(self):
        """
            If product type is rent, format name should be YEAR-VERSION-GROUP-SUBZONE-LOCK_NUMBER
            Ex: 2023-0001-1A-001 or 2023-0001-1F-T-001
        """
        names = []
        if self.year:
            names.append(self.year)
        if self.version:
            names.append(self.version)
        if self.group_id:
            names.append(self.group_id.name)
        if self.subzone:
            names.append(self.subzone)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '-'.join(names)

    @api.onchange('manual')
    def _onchange_manual(self):
        """ If select manual field, let reset width, length and area """
        self.width = 0
        self.length1 = 0
        self.area = 0

    @api.onchange('width', 'length1')
    def _onchange_width_length(self):
        """ Area = Width x Length """
        self.area = self.width * self.length1

    @api.multi
    def action_view_product(self):
        new_products = self.mapped('new_product_template_ids')
        # View Product
        action = self.env.ref('product.product_template_action').read()[0]
        action.update({
            'domain': [('id', 'in', new_products.ids)],
        })
        if len(new_products) == 1:
            action.update({
                'views': [(self.env.ref('product.product_template_only_form_view').id, 'form')],
                'res_id': new_products.id
            })
        return action
