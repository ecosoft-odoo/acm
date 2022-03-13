# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class LesseeInfoWizard(models.TransientModel):
    _name = 'lessee.info.wizard'
    _description = 'Lessee Info Wizard'

    total_partner = fields.Integer(
        compute='_compute_total_partner',
        string='Total Lessee',
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Lessee',
        readonly=True,
    )

    @api.multi
    @api.depends('partner_ids')
    def _compute_total_partner(self):
        for rec in self:
            rec.total_partner = len(rec.partner_ids)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        context = self._context.copy()
        active_model = context.get('active_model')
        active_id = context.get('active_id')
        if active_model and active_id:
            wizard = self.env[active_model].browse(active_id)
            res['partner_ids'] = [(6, 0, wizard.report_ids.mapped('partner_id').ids)]
        return res
