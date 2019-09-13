# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Tarad Agreement Contract',
    'summary': 'Tarad Contract',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/contract',
    'category': 'Agreement',
    'depends': [
        'agreement_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_analytic_account_terminate_views.xml',
        'wizard/agreement_contract_create_views.xml',
        'views/agreement_breach.xml',
        'views/res_partner.xml',
        'views/agreement_views.xml',
        'views/menus.xml',
    ],
}
