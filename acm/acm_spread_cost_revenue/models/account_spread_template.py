# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountSpreadTemplate(models.Model):
    _inherit = 'account.spread.template'

    def _prepare_spread_from_template(self, spread_account_id=False):
        res = super()._prepare_spread_from_template(
            spread_account_id=spread_account_id)
        if self._context.get('spread_over') == 'contract':
            if not self._context.get('account_analytic_id'):
                raise UserError(
                    _('Product is set to spread over contract '
                      'but no "contract/analytic" is set on invoice line'))
            res_id = self._context['account_analytic_id']
            contract = self.env['account.analytic.account'].browse(res_id)
            # Get number of period from contract end - start
            t1 = contract.date_start
            t2 = contract.date_end
            months = (t2.year - t1.year) * 12 + (t2.month - t1.month) + 1
            res['period_number'] = months
            res['force_spread_date'] = contract.date_start
        return res
