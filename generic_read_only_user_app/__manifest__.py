# -*- coding: utf-8 -*-

{
    'name': 'Generic Read Only User Access',
    "author": "Edge Technologies",
    'version': '12.0.1.0',
    'category': 'Extra Tools',
    'summary': " Generic Read only user access for particular login user.",
    'description': """ This app provides a functionality to make generic user access read only for a particular login user Set user read only
	restriction on user level. stop user access from the system .user restriction user read only restriction. Restricated user access. limited user access limited. security restriction on user level. user security restriction. 

limited access rights to user
user limited access
read only user access
user read only access
user restricted access
restriction on user access
read only user
user read only access
login user read only access
login user limited access
login user restricted access
user access restriction 
login user access restriction
user security access restriction
user security restriction
customer read only access
supplier read only access
vendor read only access
limited customer access



    """,
    "license" : "OPL-1",
    'live_test_url': "https://youtu.be/J2k28TUCbZo",
    "images":['static/description/main_screenshot.png'],
    'depends': ['base','sale_management'],
    'data': [
            'security/user_read_only_group.xml',
            'security/ir.model.access.csv',
            'views/res_user_read_only.xml',
            ],
    'installable': True,
    'auto_install': False,

}
