# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
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
        for rec in self:
            rec.age = relativedelta(fields.Date.today(), rec.date_birth).years
