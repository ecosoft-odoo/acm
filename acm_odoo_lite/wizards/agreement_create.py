# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementCreate(models.TransientModel):
    _inherit = "agreement.create"

    income_type_id = fields.Many2one(
        required=False,
    )
    partner_id = fields.Many2one(
        string="Lessee",
    )
    partner_contact_id = fields.Many2one(
        string="Lessee Contact",
    )
    lessor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor",
        required=True,
    )
    lessor_contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Lessor Contact",
    )
    post_name = fields.Char(
        required=False,
    )

    @api.multi
    def action_create_agreement(self):
        """ Create Agreement """
        self.ensure_one()
        self = self.with_context({
            "lessor_id": self.lessor_id.id,
            "lessor_contact_id": self.lessor_contact_id.id,
        })
        res = super(AgreementCreate, self).action_create_agreement()
        return res
