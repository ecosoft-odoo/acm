# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError


class TestAgreementContract(TransactionCase):

    def setUp(self):
        super(TestAgreementContract, self).setUp()
        self.agreement = self.env['agreement']
        self.agreement_analytic_account = self.env['account.analytic.account']
        self.agreement_type = self.env['agreement.type']
        self.test_partner = self.env.ref('base.res_partner_12')
        self.test_agreement_type = self.agreement_type.create({
            'name': 'Test Agreement Type',
        })

    def test_create_contract(self):
        """I create new Agreement and create new contract from this agreement.
        I expect,
         - Agreement is created.
         - Contract is created & link to Agreement.
        """
        # Create New Agreement
        with Form(self.agreement) as a:
            a.name = 'Test Agreement'
            a.description = 'Test Description'
            a.agreement_type_id = self.test_agreement_type
            a.partner_id = self.test_partner
            a.start_date = '2018-01-01'
            a.end_date = '2022-01-01'
        agreement_contract = a.save()
        # User Error Action view but not create contract yet
        with self.assertRaises(UserError):
            agreement_contract.action_view_contract()
        # Create New Contract from agreement
        agreement_contract.create_new_contract()
        # Compute contract count (Is contract created?)
        agreement_contract._compute_contract_count()
        # User Error create contract from same agreement
        with self.assertRaises(UserError):
            agreement_contract.create_new_contract()
        agreement_contract.action_view_contract()
