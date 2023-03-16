{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Eduardo",
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_salesman_views.xml',
    ],
    # 'category': 'Category',
    # 'description': """
    # Description text
    # """,
    # # data files always loaded at installation
    # 'data': [
    #     'views/mymodule_view.xml',
    # ],
    # # data files containing optionally loaded demonstration data
    # 'demo': [
    #     'demo/demo_data.xml',
    # ],
}