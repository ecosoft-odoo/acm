# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AgreementBreach(models.Model):
    _name = 'agreement.breach'

    breach_description = fields.Text(
        string='Breach Description',
    )
    date_breach = fields.Date(
        string='Breach Date',
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=False,
        copy=True,
        help="The customer or vendor this agreement is related to.",
    )
    agreement_id = fields.Many2one(
        "agreement",
        string="Agreement",
    )
