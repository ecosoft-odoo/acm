# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    market_name = fields.Char()
    market_type = fields.Char()
    market_address = fields.Char()
    fax = fields.Char()
    company_phone = fields.Char()
    show_invoice_date = fields.Boolean(
        string='Show Invoice Date (Days) ?',
        default=False,
        help="When you click this, the system will Show Invoice Date (Days) "
             "on the agreement if repeat every only 'Month(s)'",
    )

    @api.constrains('show_invoice_date')
    def _check_show_invoice_date(self):
        for rec in self:
            line = self.env['agreement.invoice.line'].search([])
            if line and not rec.show_invoice_date:
                raise UserError(
                    _("Can not uncheck Show Invoice Date (Days) ? "
                      "with existing agreement's invoice info."))
