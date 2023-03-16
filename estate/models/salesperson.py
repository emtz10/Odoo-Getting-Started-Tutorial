from odoo import api, fields, models

""" New model to inherit from users and add the property_ids field  """
class Salesperson(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many('estate.property', 'users_id', string="Properties")
