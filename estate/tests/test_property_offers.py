from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestPropertyOffers(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestPropertyOffers, cls).setUpClass()
        cls.property = cls.env['estate.property']
        cls.offer = cls.env['estate.property.offer']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Testing Partner',
            'email': 'testing_partner@example.com',
        })

    def create_property(self, name, description, postcode, expected_price, state):
        new_property = self.property.create({
            'name': name,
            'description': description,
            'postcode': postcode,
            'expected_price': expected_price,
            'state': state,
        })
        return new_property

    def create_offer(self, price, partner, property):
        new_offer = self.offer.create({
            'price': price,
            'partner_id': partner,
            'property_id': property,
        })
        return new_offer

    def test_create_offer_for_sold_property(cls):
        """ Test that offers can't be created when
            a property is sold. """
        property = cls.create_property('Big Dept.',
                                          'Dept. with 2 bedrooms',
                                          12345, 1000.00, 'sold')
        with cls.assertRaises(UserError, msg="You can't create offers for \
                              sold properties"):
            cls.create_offer(1000.00, cls.partner, property.id)

