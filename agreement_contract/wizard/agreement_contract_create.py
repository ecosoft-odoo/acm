from odoo import models, api, _
from odoo.exceptions import UserError


class AgreementContractCreate(models.TransientModel):
    _name = 'agreement.contract.create'
    _description = 'Create contract the selected agreement'

    @api.multi
    def create_contract(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        for record in self.env['agreement'].browse(active_ids):
            if record.contract_count != 0:
                raise UserError(
                    _("Selected Agreement(s) cannot be create "
                      "as they have contract already."))
            record.create_new_contract()
