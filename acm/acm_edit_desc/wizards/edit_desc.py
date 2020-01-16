# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EditDesc(models.TransientModel):
    _name = 'edit.desc'

    name = fields.Text(
        string='Description',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditDesc, self).default_get(fields)
        if not self._context.get('edit_field', False):
            raise UserError(_('No edit_field context passed!'))
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        res['name'] = rec[self._context['edit_field']]
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        if not self._context.get('edit_field', False):
            raise UserError(_('No edit_field context passed!'))
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        rec = self.env[active_model].browse(active_id)
        rec.write({self._context['edit_field']: self.name})
        return True
