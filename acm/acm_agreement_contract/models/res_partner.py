# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    date_birth = fields.Date(
        string='Birth Date',
    )
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
    )

    @api.multi
    def _compute_age(self):
        for record in self:
            record.age = relativedelta(
                fields.Date.today(), record.date_birth).years
