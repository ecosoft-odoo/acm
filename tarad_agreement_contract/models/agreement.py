# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class Agreement(models.Model):
    _inherit = 'agreement'

    contract_genre = fields.Selection(
        [('lease', 'Lease'),
         ('extension', 'Extension'),
         ('termination', 'Termination'),
         ('breach', 'Breach'),
         ('transfer', 'Transfer'),
         ],
        default='lease',
    )
    extension_agreement_id = fields.Many2one(
        'agreement',
        string="Source Agreement",
        readonly=True,
    )
    breach_ids = fields.One2many(
        'agreement.breach',
        'agreement_id',
        string='Breach',
    )
    breach_agreement = fields.Boolean(
        string='Breach Agreement',
    )
    breach_description = fields.Text(
        string='Breach Description',
    )
    transfer_agreement_id = fields.Many2one(
        'agreement',
        string='Agreement',
        readonly=True,
    )
    date_breach = fields.Date(
        string='Breach Date',
    )

    # @api.multi
    # def action_view_contracts(self):
    #     self.ensure_one()
    #     action_id = 'contract.action_account_analytic_%s_overdue_all' \
    #         % (self.contract_type)
    #     action = self.env.ref(action_id).read()[0]
    #     view_id = 'contract.account_analytic_account_%s_form' \
    #         % (self.contract_type)
    #     action.update({
    #         'views': [(self.env.ref(view_id).id, 'form')],
    #         'res_id': self.id,
    #     })
    #     return action
