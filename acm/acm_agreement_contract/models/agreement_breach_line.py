# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class AgreementBreachLine(models.Model):
    _name = 'agreement.breach.line'

    agreement_id = fields.Many2one(
        comodel_name='agreement',
    )
    date_breach = fields.Date(
        string='Breach Date',
    )
    type_breach = fields.Char(
        string='Breach Type',
    )
    reason_breach = fields.Char(
        string='Breach Reason',
    )
    date_cancel_breach = fields.Date(
        string='Cancel Breach Date',
    )
    reason_cancel_breach = fields.Char(
        string='Cancel Breach Reason',
    )
