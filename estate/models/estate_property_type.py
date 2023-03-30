""" Estate property types catalog """
from odoo import api, fields, models


class EstatePropertyType(models.Model):
    # -------- Private Attributes --------
    _name = "estate.property.type"
    _description = "Real Estate Property Type Data"
    _order = "sequence, name"
    _sql_constraints = [
        ('check_type_name', 'UNIQUE(name)',
         'Type name must be unique!')
    ]

    # -------- Fields Declaration --------
    name = fields.Char(required=True)
    property_id = fields.One2many("estate.property", "property_type_id", string="Property")
    sequence = fields.Integer(default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_count_offers")

    # -------- Compute Methods --------
    @api.depends("offer_ids")
    def _compute_count_offers(self):
        """ Returns the number of total offers linked to
            the property type """
        for record in self:
            record.offer_count = len(record.offer_ids)

    # -------- Action Methods --------
    # Action for stat button
    # With this, there is no need to create the action in views
    def action_redirect_to_offers(self):
        """ Returns view configuration for the offers
            linked to the property type """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Offers',
            'view_mode': 'tree',
            'res_model': 'estate.property.offer',
            'domain': [('property_type_id', '=', self.id)],
            'context': "{'create': False}"
        }
