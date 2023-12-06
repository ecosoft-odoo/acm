# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, api, models, _
from odoo.exceptions import UserError


class ACMProductPricelist(models.Model):
    _name = 'acm.product.pricelist'
    _description = 'Product Pricelist For ACM'
    _order = 'is_lastest_version desc, group_id, lock_number, subzone'

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Pricelist Name',
        required=True,
        index=True,
        ondelete='restrict',
    )
    name = fields.Char()
    year = fields.Selection(
        selection=lambda self: self._get_selection_year(),
        string='Year',
        related='product_template_id.year',
        store=True,
    )
    version = fields.Selection(
        selection=lambda self: self._get_selection_version(),
        string='Version',
        related='product_template_id.version',
        store=True,
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
        related='product_template_id.group_id',
        store=True,
        index=True,
        ondelete='restrict',
    )
    subzone = fields.Char(
        string='Subzone',
        related='product_template_id.subzone',
        store=True,
    )
    lock_number = fields.Char(
        string='Number',
        related='product_template_id.lock_number',
        store=True,
    )
    is_lastest_version = fields.Boolean(
        string='Is Lastest Version',
        related='product_template_id.is_lastest_version',
        store=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    item_ids = fields.One2many(
        comodel_name='acm.product.pricelist.item',
        inverse_name='pricelist_id',
        string='Item Pricelist',
        copy=True,
    )

    @api.model
    def _get_selection_year(self):
        year_selection = [(str(year), str(year)) for year in range(2020, 2060)]
        return year_selection

    @api.model
    def _get_selection_version(self):
        version_selection = [(str(i).zfill(4), str(i).zfill(4)) for i in range(1, 10)]
        return version_selection

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        # Search Product Template
        product_template_id = self._context['default_product_template_id'] if self._context.get('default_product_template_id') else self.product_template_id.id
        product_template = self.env['product.template'].browse(product_template_id)
        # Search Item Description
        item_descriptions = self.env['acm.product.pricelist.item.description'].search([])
        # ค่าเช่า, ค่าบริการ
        item_description_1 = item_descriptions.filtered(lambda k: 'ค่าเช่า' in k.name or 'ค่าบริการ' in k.name)
        # อื่นๆ
        item_description_2 = item_descriptions - item_description_1
        # --
        self.item_ids = False
        vals = []
        for product in product_template.product_variant_ids:
            for id in item_description_1:
                vals.append((0, 0, {'product_id': product.id, 'name': id.id, 'lst_price': 0.0}))
        for id in item_description_2:
            p = self.env['product.product'].search([('name', '=', id.name)], limit=1)
            if p:
                vals.append((0, 0, {'product_id': p.id, 'name': id.id, 'manual': True, 'lst_price': 0.0}))
        self.item_ids = vals

    @api.constrains('product_template_id')
    def _check_product_template_id(self):
        for rec in self:
            pricelist_count = rec.with_context({'active_test': False}).search_count(
                [('product_template_id', '=', rec.product_template_id.id)])
            if pricelist_count > 1:
                raise UserError(_('Multiple pricelist not allowed on the product.'))

    @api.model
    def create(self, vals):
        if vals.get('product_template_id'):
            # Update name for reference pricelist
            pt = self.env['product.template'].browse(vals['product_template_id'])
            vals['name'] = pt.name
        return super(ACMProductPricelist, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('product_template_id'):
            # Update name for reference pricelist
            pt = self.env['product.template'].browse(vals['product_template_id'])
            vals['name'] = pt.name
        return super(ACMProductPricelist, self).write(vals)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = u'{}'.format(rec.product_template_id.name)
    #         res.append((rec.id, name))
    #     return res

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     domain = args or []
    #     domain += [('product_template_id.name', operator, name)]
    #     return self.search(domain, limit=limit).name_get()


class ACMProductPricelistItemDescription(models.Model):
    _name = 'acm.product.pricelist.item.description'
    _description = 'Product Pricelist Item Description For ACM'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    condition = fields.Text(
        string='Condition',
        help="""
            This field will match with condition on the agreement \n
            Condition use python code, for the example -> agreement.recurring_rule_type == 'monthly'
        """,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=1,
    )

    @api.constrains('condition')
    def _check_condition(self):
        for rec in self:
            # Test that condition field is correct.
            agreement = self.env['agreement']
            if rec.condition:
                try:
                    eval(rec.condition)
                except Exception:
                    raise UserError(_('Condition is wrong, please check it.'))


class ACMProductPricelistItem(models.Model):
    _name = 'acm.product.pricelist.item'
    _description = 'Product Pricelist Item For ACM'
    _order = 'is_lastest_version desc, group_id, lock_number, subzone, pricelist_id, id'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        index=True,
        ondelete='restrict',
    )
    name = fields.Many2one(
        comodel_name='acm.product.pricelist.item.description',
        string='Description',
        required=True,
        index=True,
        ondelete='restrict',
    )
    manual = fields.Boolean(
        string='Manual',
        default=False,
    )
    price_per_square_meter = fields.Float(
        string='Price / Square Meter',
        compute='_compute_price_per_square_meter',
        store=True,
    )
    square_meter_per_price = fields.Float(
        string='Square Meter / Price',
        compute='_compute_square_meter_per_price',
        store=True,
    )
    lst_price = fields.Float(
        string='Unit Price',
        default=0.0,
    )
    condition = fields.Text(
        string='Condition',
        related='name.condition',
        store=True,
    )
    pricelist_id = fields.Many2one(
        comodel_name='acm.product.pricelist',
        string='Pricelist Name',
        ondelete='cascade',
        index=True,
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
        related='pricelist_id.group_id',
        store=True,
        index=True,
        ondelete='restrict',
    )
    lock_number = fields.Char(
        string='Number',
        related='pricelist_id.lock_number',
        store=True,
    )
    subzone = fields.Char(
        string='Subzone',
        related='pricelist_id.subzone',
        store=True,
    )
    is_lastest_version = fields.Boolean(
        string='Is Lastest Version',
        related='pricelist_id.is_lastest_version',
        store=True,
    )

    @api.multi
    @api.depends(
        'pricelist_id',
        'pricelist_id.product_template_id',
        'pricelist_id.product_template_id.area',
        'lst_price'
    )
    def _compute_price_per_square_meter(self):
        for rec in self:
            product_template = rec.pricelist_id.product_template_id
            product_area = product_template.area
            if product_area:
                rec.price_per_square_meter = rec.lst_price / product_area
            else:
                rec.price_per_square_meter = 0

    @api.multi
    @api.depends(
        'pricelist_id',
        'pricelist_id.product_template_id',
        'pricelist_id.product_template_id.area',
        'lst_price'
    )
    def _compute_square_meter_per_price(self):
        for rec in self:
            product_template = rec.pricelist_id.product_template_id
            product_area = product_template.area
            if rec.lst_price:
                rec.square_meter_per_price = product_area / rec.lst_price
            else:
                rec.square_meter_per_price = 0
