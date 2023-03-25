{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Eduardo",
    'installable': True,
    'application': True,
    'demo': [
        'demo/estate_demo.xml',
    ],
    'data': [
        'data/estate.property.type.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_salesman_views.xml',
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
    ],
    'category': 'Real Estate/Brokerage',
}