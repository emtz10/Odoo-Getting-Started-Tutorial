from odoo import models, Command

""" New model to inherit from users and add the property_ids field  """
class EstateProperty(models.Model):
    _inherit = "estate.property"

    """
        Adds functionality to create invoices when selling properties.
        Command is used to create One2many and Many2many records.
    """
    def action_sell_property(self):
        self.ensure_one()
        super(EstateProperty, self).action_sell_property()
        self.env['account.move'].create({
            "partner_id": self.partner_id.id,
            "move_type": "out_invoice",
            "line_ids": [
                Command.create({
                    "name": "Services",
                    "quantity": 1,
                    "price_unit": (self.selling_price * 0.06),
                }),
                Command.create({
                    "name": "Administrative Fees",
                    "quantity": 1,
                    "price_unit": 100,
                })
            ],
        })
        return True
