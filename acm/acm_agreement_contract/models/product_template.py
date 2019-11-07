# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float()
    length = fields.Float()
    area = fields.Float()
    working_hours = fields.Char()
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('tea_money', 'Tea Money'),
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
    zone = fields.Char(
        string='Zone',
    )
    lock_number = fields.Char(
        string='Number',
    )

    @api.onchange('zone', 'lock_number')
    def _onchange_zone_number(self):
        names = []
        if self.zone:
            names.append(self.zone)
        if self.lock_number:
            names.append(self.lock_number)
        self.name = '/'.join(names)
