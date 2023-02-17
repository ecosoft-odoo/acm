# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "ACM :: Odoo Lite",
    "version": "12.0.1.0.0",
    "author": "Ecosoft",
    "license": "AGPL-3",
    "category": "Agreement",
    "depends": ["acm"],
    "data": [
        "data/menu.xml",
        "data/agreement_data.xml",
        "data/agreement_sections_data.xml",
        "data/agreement_clauses_data.xml",
        "views/account_analytic_account_views.xml",
        "views/agreement_views.xml",
        "views/agreement_income_type_views.xml",
        "views/res_partner_views.xml",
        "views/product_views.xml",
        "wizards/agreement_create_wizards.xml",
        "wizards/agreement_create_contract_wizards.xml",
        "wizards/agreement_extension_wizards.xml",
        "report/occupancy_land_analysis_report.xml",
    ]
}
