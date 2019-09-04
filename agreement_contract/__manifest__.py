# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Agreements Contract",
    "summary": "",
    "version": "12.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/contract",
    'category': 'Agreement',
    "depends": [
        "contract",
        'agreement_legal',
    ],
    "data": [
        "views/agreement.xml",
        "views/account_analytic_account_view.xml",
    ],
}
