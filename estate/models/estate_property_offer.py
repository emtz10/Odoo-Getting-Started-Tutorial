""" Offers made to properties """

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class EstatePropertyOffer(models.Model):
    # -------- Private Attributes --------
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"
    # Adding constrains using sql
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)',
         'Price must be greater than zero!')
    ]

    # -------- Fields Declaration --------
    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline',  store=True)
    # This field is needed for stat button functionality
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    # -------- Compute Methods --------
    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = (record.create_date if record.create_date else datetime.now().date()) + relativedelta(days=record.validity)

    # This method works similar as the compute method as it update the field values based on another field
    # This method only works after save a record
    def _inverse_deadline(self):
        for record in self:
            record.validity = relativedelta(record.date_deadline, record.create_date.date()).days

    # -------- Action Methods --------
    # Actions related to buttons in view
    def action_confirm_offer(self):
        """ Confirm offer when property state is not selected or is offer_received or new.
            This is the only way to update selling price.
            This method link the buyer with the property """
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

    def action_cancel_offer(self):
        """ Cancel offer only when no status is selected """
        for record in self:
            if record.status is False:
                record.status = 'refused'
            else:
                raise UserError("You can't cancel this offer")
        return True

    # -------- CRUD Methods --------
    @api.model
    def create(self, vals):
        """ Add validations when creating new records to avoid
            offers with lower price than the current ones
            and also updates the state of the property when creating
            the first offer.
        """
        offer = self.env['estate.property.offer'].search([
            ('price', '>', vals['price']),
            ('property_id', '=', vals['property_id'])
        ], order="price desc", limit=1)
        if offer:
            raise UserError(f"You can't create an offer lower than {offer[0].price}")

        if self.env['estate.property'].browse(vals['property_id']).state == 'new':
            self.env['estate.property'].browse(vals['property_id']).state = 'offer_received'
        return super().create(vals)