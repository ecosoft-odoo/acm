# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    market_name = fields.Char()
    market_type = fields.Char()
    market_address = fields.Char()
    fax = fields.Char()
    company_phone = fields.Char()
