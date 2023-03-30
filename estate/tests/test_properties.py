from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError


class TestProperties(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestProperties, cls).setUpClass()
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

    def test_sold_property_without_accepted_offers(self):
        """ Test that properties without accepted offers can't be
            sold. """
        property = self.create_property('Big Dept.',
                                        'Dept. with 2 bedrooms',
                                        12345, 1000.00, 'new')
        with self.assertRaises(UserError, msg="You can't sell a property \
                              without offers"):
            property.action_sell_property()

    def test_property_status_changed_after_sold(self):
        """ Test that property state change after been sold. """
        property = self.create_property('Big Dept.',
                                        'Dept. with 2 bedrooms',
                                        12345, 1000.00, 'new')
        new_offer = self.create_offer(1000.00, self.partner.id, property.id)
        new_offer.action_confirm_offer()
        property.action_sell_property()
        self.assertEqual(property.state, 'sold')

    def test_set_and_reset_of_garden_area_and_orientation(self):
        """ Test that values of garden area and garden orientation
            change to default values when garden is selected and
            reset after been deselected."""
        f = Form(self.env['estate.property'])
        f.garden = True
        self.assertEqual(f.garden_area, 10)
        self.assertEqual(f.garden_orientation, 'north')
        f.garden = False
        self.assertEqual(f.garden_area, 0)
        self.assertEqual(f.garden_orientation, False)
