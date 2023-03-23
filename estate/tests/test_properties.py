from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError

class TestProperties(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestProperties, cls).setUpClass()
        cls.property = cls.env['estate.property']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Testing Partner',
            'email': 'testing_partner@example.com',
        })

    def test_sold_property_without_accepted_offers(cls):
        """ Test that properties without accepted offers can't be
            sold. """
        property = cls.create_property('Big Dept.',
                                          'Dept. with 2 bedrooms',
                                          12345, 1000.00, 'new')
        with cls.assertRaises(UserError, msg="You can't sell a property \
                              without offers"):
            property.action_sell_property()

    def test_property_status_changed_after_sold(cls):
        """ Test that property state change after been sold. """
        property = cls.create_property('Big Dept.',
                                        'Dept. with 2 bedrooms',
                                        12345, 1000.00, 'new')
        new_offer = cls.create_offer(1000.00, cls.partner.id, property.id)
        new_offer.action_confirm_offer()
        property.action_sell_property()
        cls.assertEqual(property.state, 'sold')

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