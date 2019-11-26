# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float()
    length = fields.Float()
    area = fields.Float(
        compute='_compute_area',
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

    @api.depends('width', 'length')
    def _compute_area(self):
        for rec in self:
            rec.area = rec.width * rec.length

    @api.onchange('group_id', 'lock_number')
    def _onchange_group_number(self):
        names = []
        if self.group_id:
            names.append(self.group_id.name)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '/'.join(names)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    area = fields.Float(
        compute='_compute_area',
    )

    @api.depends('width', 'length')
    def _compute_area(self):
        for rec in self:
            rec.area = rec.width * rec.length

    @api.onchange('group_id', 'lock_number')
    def _onchange_group_number(self):
        names = []
        if self.group_id:
            names.append(self.group_id.name)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '/'.join(names)
