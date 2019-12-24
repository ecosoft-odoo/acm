# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float()
    length1 = fields.Float(
        string='Length',
    )
    area = fields.Float(
        compute='_compute_area',
        string='Area (Auto)',
    )
    working_hours_id = fields.Many2one(
        comodel_name='acm.working.hours',
        string='Working Hours',
        domain="[('type', '=', 'in_time')]",
    )
    working_hours2_id = fields.Many2one(
        comodel_name='acm.working.hours',
        string='Not Working Hours',
        domain="[('type', '=', 'out_time')]",
    )
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('lump_sum_rent', 'Lump Sum Rent'),
            ('security_deposit', 'Security Deposit'),
            ('transfer', 'Transfer'), ],
        string='Value Type',
    )
    goods_type = fields.Char(
        string='Goods Type',
    )
    goods_category_id = fields.Many2one(
        comodel_name='goods.category',
        string='Goods Category',
    )
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
    manual_area = fields.Float(
        string='Area (Manual)',
    )
    lease_area = fields.Float(
        compute='_compute_lease_area',
        string='Area For Lease',
        help='Calculate from area (auto) or area (manual)',
    )
    occupied_area = fields.Float(
        compute='_compute_occupied_area',
        string='Area Occupied',
    )
    occupancy = fields.Float(
        compute='_compute_occupancy',
        string='Occupancy',
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]

    @api.depends('width', 'length1')
    def _compute_area(self):
        for rec in self:
            rec.area = rec.width * rec.length1

    @api.depends('area', 'manual', 'manual_area')
    def _compute_lease_area(self):
        for rec in self:
            rec.lease_area = rec.manual and rec.manual_area or rec.area

    @api.multi
    def _compute_occupied_area(self):
        Product = self.env['product.product']
        Agreement = self.env['agreement']
        now = fields.Date.today()
        for rec in self:
            product = Product.search([('product_tmpl_id', '=', rec.id)])
            agreement = Agreement.search([
                ('rent_product_id', '=', product.id),
                ('state', '=', 'active'),
                ('start_date', '<=', now),
                ('end_date', '>=', now), ])
            if agreement:
                rec.occupied_area = rec.lease_area

    @api.multi
    def _compute_occupancy(self):
        total_lease_area = sum(self.search([]).mapped('lease_area'))
        for rec in self:
            rec.occupancy = (rec.occupied_area / total_lease_area) * 100

    @api.onchange('group_id', 'lock_number')
    def _onchange_group_number(self):
        names = []
        if self.group_id:
            names.append(self.group_id.name)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '-'.join(names)

    @api.onchange('manual')
    def _onchange_manual(self):
        self.width = 0
        self.length1 = 0
        self.manual_area = 0

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(ProductTemplate, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        for line in res:
            if '__domain' in line:
                product = self.search(line['__domain'])
                line['lease_area'] = sum(product.mapped('lease_area'))
                line['occupied_area'] = sum(product.mapped('occupied_area'))
                line['occupancy'] = sum(product.mapped('occupancy'))
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    area = fields.Float(
        compute='_compute_area',
    )

    @api.depends('width', 'length1')
    def _compute_area(self):
        for rec in self:
            rec.area = rec.width * rec.length1

    @api.onchange('group_id', 'lock_number')
    def _onchange_group_number(self):
        names = []
        if self.group_id:
            names.append(self.group_id.name)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '-'.join(names)

    @api.onchange('manual')
    def _onchange_manual(self):
        self.width = 0
        self.length1 = 0
        self.manual_area = 0
