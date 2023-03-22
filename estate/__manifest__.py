{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Eduardo",
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'security/estate_security.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_salesman_views.xml',
    ],
    'category': 'Real Estate/Brokerage',
}