# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Tarad Agreement Contract",
    "summary": "test",
    "version": "12.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/contract",
    'category': 'Agreement',
    "depends": [
        'agreement_contract',
    ],
    "data": [
        "wizard/account_analytic_account_create_views.xml",
        "views/account_analytic_account_views.xml",
        "views/agreement_views.xml",
        "views/agreement_clause_views.xml",
        "views/agreement_section_views.xml",
    ],
}
