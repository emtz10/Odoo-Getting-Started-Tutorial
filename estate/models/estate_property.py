"""" Real Estate Property module for Odoo 16 """

"""" Import packages from Odoo """
from odoo import fields, models
"""" Import date and time libraries """
from datetime import datetime
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    """" Set name to table in database, `.` converts to `_` """
    _name = "estate.property"
    _description = "Real Estate Property Data"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    postcode = fields.Char(required=True)
    """" Relativedelta allows to add time by months because datetime only allows by days """
    date_availability = fields.Date('Date Availability', default=datetime.now() + relativedelta(months=3), copy=False)
    expected_price = fields.Float('Expected price', digits=(10,1), required=True)
    """" 'Copy' parameter defines if the value of the field can be copied when duplicated """
    selling_price = fields.Float('Selling price', digits=(10,1), readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer('Living area')
    facades = fields.Integer()
    garage = fields.Boolean(default=False)
    garden = fields.Boolean(default=False)
    garden_area = fields.Integer('Garden area')
    garden_orientation =  fields.Selection(string='Garden orientation', selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    property_type_id = fields.Many2one(string="Property Type", comodel_name='estate.property.type')
    users_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    property_tag_id = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    """" Adding reserved fields to table """
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='Status',
        selection=([
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold_and_canceled', 'Sold and Canceled')
        ]), required=True, copy=False, default='new'
    )


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type Data"

    name = fields.Char(required=True)


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    name = fields.Char(required=True)


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)