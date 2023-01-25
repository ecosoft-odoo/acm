# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner",

    lessor = fields.Boolean(
        string="Is a Lessor",
        default=False,
    )
    sequence_code = fields.Char(
        string="Sequence Code",
    )
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        index=True,
        readonly=True,
        ondelete="restrict",
    )

    @api.constrains("sequence_code")
    def _check_sequence_code(self):
        for rec in self:
            if rec.sequence_code and len(rec.sequence_code) != 3:
                raise UserError(_("The sequence code must be equal to 3 characters."))

    @api.multi
    def _create_update_sequence(self):
        self.ensure_one()
        is_lessor = self.lessor
        sequence_code = self.sequence_code
        if is_lessor and sequence_code:
            if not self.sequence_id:
                sequence = self.env["ir.sequence"].sudo().create({
                    "name": "Agreement - {}".format(sequence_code),
                    "code": sequence_code,
                    "implementation": "no_gap",
                    "prefix": "{}-%(year)s-".format(sequence_code),
                    "padding": 4,
                    "number_increment": 1,
                    "use_date_range": True,
                })
                self.write({"sequence_id": sequence.id})
            elif sequence_code != self.sequence_id.code:
                self.sequence_id.sudo().write({
                    "name": "Agreement - {}".format(sequence_code),
                    "code": sequence_code,
                    "prefix": "{}-%(year)s-".format(sequence_code),
                })
        return True

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        # Create or update sequence
        partner._create_update_sequence()
        return partner

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for partner in self:
            # Create or update sequence
            partner._create_update_sequence()
        return res
