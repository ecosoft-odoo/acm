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
    partner_type = fields.Selection(
        selection=[
            ('active_lessee', 'Active Lessee'),
            ('inactive_lessee', 'Inactive Lessee'),
            ('prospective_lessee', 'Prospective Lessee'), ],
        compute='_compute_partner_type',
        string='Type',
        store=True,
    )
    agreement_number = fields.Integer(
        string='No. of Active Leases',
        compute='_compute_agreement_number',
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique!'),
    ]

    @api.depends('agreement_ids', 'agreement_ids.state')
    def _compute_partner_type(self):
        for rec in self:
            agreements = rec.agreement_ids
            if not agreements:
                continue
            if agreements.filtered(lambda l: l.state == 'active'):
                rec.partner_type = 'active_lessee'
            else:
                rec.partner_type = 'inactive_lessee'

    @api.multi
    def _compute_age(self):
        for rec in self:
            rec.age = relativedelta(fields.Date.today(), rec.date_birth).years

    @api.multi
    def _compute_agreement_number(self):
        for rec in self:
            rec.agreement_number = len(rec.agreement_ids.filtered(
                lambda l: l.state == 'active'))

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(ResPartner, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        if 'agreement_number' in fields:
            for line in res:
                if '__domain' in line:
                    line['agreement_number'] = \
                        sum(self.search(line['__domain'])
                            .mapped('agreement_number'))
        return res
