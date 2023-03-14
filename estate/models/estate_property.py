"""" Real Estate Property module for Odoo 16 """

"""" Import packages from Odoo """
from odoo import api, fields, models
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
    offer_id = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_offer')
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

    # Computed fields
    # Adding dependencies to decorator
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            # Updating field with sum of values
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_id.price")
    def _compute_best_offer(self):
        for offer in self:
            offer.best_price = max(self.mapped('offer_id.price')) if self.mapped('offer_id.price') else 0

    # Onchange method to update field values when another field is updated
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''



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
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline',  store=True)

    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = (record.create_date if record.create_date else datetime.now().date()) + relativedelta(days=record.validity)

    # This method works similar as the compute method as it update the field values based on another field
    # This method only works after save a record
    def _inverse_deadline(self):
        for record in self:
            record.validity = relativedelta(record.date_deadline, record.create_date.date()).days