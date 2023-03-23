{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Eduardo",
    'installable': True,
    'application': True,
    'data': [
        'data/estate.property.type.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_salesman_views.xml',
        'security/estate_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/estate_demo.xml',
    ],
    'category': 'Real Estate/Brokerage',
}