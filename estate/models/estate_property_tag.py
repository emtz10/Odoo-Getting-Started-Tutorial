""" Estate property tags catalog """
from odoo import api, fields, models


class EstatePropertyTag(models.Model):
    # -------- Private Attributes --------
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"
    _sql_constraints = [
        ('check_tag_name', 'UNIQUE(name)',
         'Tag name must be unique!')
    ]

    # -------- Fields Declaration --------
    name = fields.Char(required=True)
    color = fields.Integer()
