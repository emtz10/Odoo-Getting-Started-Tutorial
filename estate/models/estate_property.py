"""" Real Estate Property module for Odoo 16 """

from datetime import datetime
from dateutil.relativedelta import relativedelta
"""" Import packages from Odoo """
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


""" Estate properties main model """
class EstateProperty(models.Model):
    # -------- Private Attributes --------
    # Set name to table in database, `.` converts to `_`
    _name = "estate.property"
    _description = "Real Estate Property Data"
    _order = "id desc"
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
         'Expected price must be greater than zero!'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
         'Selling price must be positive!'),
    ]

    # -------- Fields Declaration --------
    name = fields.Char(required=True)
    description = fields.Char(required=True)
    postcode = fields.Char(required=True)
    # Relativedelta allows to add time by months because datetime only allows by days
    date_availability = fields.Date('Date Availability', default=datetime.now() + relativedelta(months=3), copy=False)
    expected_price = fields.Float('Expected price', digits=(10,1), required=True)
    # 'Copy' parameter defines if the value of the field can be copied when duplicated
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
    property_type_id = fields.Many2one(string="Property Type",
        comodel_name='estate.property.type')
    users_id = fields.Many2one('res.users', string='Salesman',
        default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer',
        copy=False)
    property_tag_id = fields.Many2many('estate.property.tag',
        string="Tags")
    offer_id = fields.One2many("estate.property.offer", "property_id",
        string="Offers")
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_offer')
    company_id = fields.Many2one('res.company', string='Company',
        required=True, default=lambda self: self.env.company)
    # Adding reserved fields to table
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

   # -------- Compute Methods --------
    # Adding dependencies to decorator
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        """ Updating field with sum of living and garden areas """
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_id.price")
    def _compute_best_offer(self):
        """ Gets highest price from offers """
        for offer in self:
            offer.best_price = max(self.mapped('offer_id.price')) \
                if self.mapped('offer_id.price') else 0

    # -------- Constrains and Onchange Methods --------
    @api.onchange("garden")
    def _onchange_garden(self):
        """ Sets default values when garden is selected """
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # Adding constrains using Python code
    @api.constrains('selling_price')
    def _check_selling_price(self):
        """ Checks if selling price is lower than 90% of expected price """
        for record in self:
            if float_compare(record.selling_price, (record.expected_price * 0.9), 2) < 0 \
                and float_is_zero(record.selling_price, 2) is False:
                raise ValidationError("Selling price can't be lower than 90% of expected price")

    # -------- Action Methods --------
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
                if 'accepted' not in record.mapped('offer_id.status'):
                    raise UserError("You can't sell a property without offers")
                record.state = 'sold'
            else:
                raise UserError("You can't change the status of this property")
        return True

    # -------- CRUD Methods --------
    @api.ondelete(at_uninstall=False)
    def _unlink_except_if_state_is_new_or_canceled(self):
        """ Adds validations when deleting records with state different to
            new or canceled.
        """
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("Properties with offers can't be deleted")