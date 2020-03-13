# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class ImportXLSXWizard(models.TransientModel):
    _inherit = 'import.xlsx.wizard'

    @api.multi
    def action_import(self):
        self.ensure_one()
        context = self._context.copy()
        if context.get('active_model') == 'acm.batch.invoice':
            active_id = self._context.get('active_id')
            batch = self.env['acm.batch.invoice'].browse(active_id)
            context.update({
                'name': batch.name,
                'group_id': batch.group_id.id,
                'date_range_id': batch.date_range_id.id,
            })
        self = self = self.with_context(context)
        return super(ImportXLSXWizard, self).action_import()
