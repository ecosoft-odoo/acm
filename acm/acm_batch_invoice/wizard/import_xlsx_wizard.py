# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning


class ImportXLSXWizard(models.TransientModel):
    _inherit = 'import.xlsx.wizard'

    @api.multi
    def action_import(self):
        self.ensure_one()
        batch = self.env['acm.batch.invoice'].browse(
            self._context.get('active_id')
        )
        self = self.with_context({
            'name': batch.name,
            'zone': batch.group_id.name,
            'date_name': batch.date_range_id.name,
        })
        return super(ImportXLSXWizard, self).action_import()
