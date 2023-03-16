"""" Real Estate Property module for Odoo 16 """

"""" Import date and time libraries """
from datetime import datetime
from dateutil.relativedelta import relativedelta
"""" Import packages from Odoo """
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


""" Estate properties main model """
class EstateProperty(models.Model):
    """" Set name to table in database, `.` converts to `_` """
    _name = "estate.property"
    _description = "Real Estate Property Data"
    _order = "id desc"

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
    garden_orientation =  fields.Selection(string='Garden orientation', selection=[
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ])
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
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ]), required=True, copy=False, default='new'
    )

    """ Computed fields """
    """ Adding dependencies to decorator """
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            """ Updating field with sum of values """
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_id.price")
    def _compute_best_offer(self):
        for offer in self:
            offer.best_price = max(self.mapped('offer_id.price')) if self.mapped('offer_id.price') else 0

    """ Onchange method to update field values when another field is updated """
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    """ Actions """
    def action_cancel_property(self):
        for record in self:
            if record.state != 'sold' and record.state != 'canceled':
                record.state = 'canceled'
            else:
                raise UserError("You can't change the status of this property")
        return True

    def action_sell_property(self):
        for record in self:
            if record.state != 'canceled' and record.state != 'sold':
                record.state = 'sold'
            else:
                raise UserError("You can't change the status of this property")
        return True

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
         'Expected price must be greater than zero!'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
         'Selling price must be positive!'),
    ]

    """ Adding constrains using Python code """
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if float_compare(record.selling_price, (record.expected_price * 0.9), 2) < 0 \
                and float_is_zero(record.selling_price, 2) is False:
                raise ValidationError("Selling price can't be lower than 90% of expected price")


""" Estate property types catalog """
class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type Data"
    _order = "sequence, name"

    name = fields.Char(required=True)
    property_id = fields.One2many("estate.property", "property_type_id", string="Property")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_count_offers")

    """ Compute method to count offers related to property type """
    @api.depends("offer_ids")
    def _compute_count_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    """ Action for stat button, with this, there is no need to create the action in views """
    def action_redirect_to_offers(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Offers',
                'view_mode': 'tree',
                'res_model': 'estate.property.offer',
                'domain': [('property_type_id', '=', self.id)],
                'context': "{'create': False}"
            }

    _sql_constraints = [
        ('check_type_name', 'UNIQUE(name)',
         'Type name must be unique!')
    ]


""" Estate property tags catalog """
class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('check_tag_name', 'UNIQUE(name)',
         'Tag name must be unique!')
    ]


""" Offers made to properties """
class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline',  store=True)
    """ This field is needed for stat button functionality """
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = (record.create_date if record.create_date else datetime.now().date()) + relativedelta(days=record.validity)

    """ This method works similar as the compute method as it update the field values based on another field """
    """ This method only works after save a record """
    def _inverse_deadline(self):
        for record in self:
            record.validity = relativedelta(record.date_deadline, record.create_date.date()).days

    """ Actions related to buttons in view """
    """ Confirm offer when property state is not selected or is offer_received or new """
    """ This is the only way to update selling price """
    """ This method link the buyer with the property """
    def action_confirm_offer(self):
        for record in self:
            if record.property_id.state not in ['offer_accepted', 'sold', 'canceled'] \
                and float_is_zero(record.property_id.selling_price, 2):
                record.status = 'accepted'
                record.property_id.selling_price = record.price
                record.property_id.partner_id = record.partner_id
                record.property_id.state = 'offer_accepted'
            else:
                raise UserError("You can't accept the offer")
        return True

    """ Cancel offer only when no status is selected """
    def action_cancel_offer(self):
        for record in self:
            if record.status is False:
                record.status = 'refused'
            else:
                raise UserError("You can't cancel this offer")
        return True

    """ Adding constrains using sql """
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)',
         'Price must be greater than zero!')
    ]