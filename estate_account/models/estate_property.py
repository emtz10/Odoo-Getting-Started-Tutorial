""" Class to inherit from 'estate.property' model in estate module  """

from odoo import models, Command


class EstateProperty(models.Model):
    """ This class inherits from 'estate.property' model of
        the estate module """

    # -------- Private Attributes --------
    _inherit = "estate.property"

    # -------- Action Methods --------
    # This method overrides 'action_sell_property' from 'estate.property' model
    def action_sell_property(self):
        """ Inherits from action_sell_property method of
            the estate module to add the invoice creation
            functionality when selling properties """
        self.check_access_rights('update')
        self.check_access_rule('update')

        res = super(EstateProperty, self).action_sell_property()
        # Get journal value to create an invoice
        journal = self.env["account.journal"].sudo().search([("type", "=", "sale")], limit=1)
        for record in self:
            self.env['account.move'].sudo().create({
                "partner_id": record.partner_id.id,
                "move_type": "out_invoice",
                "journal_id": journal.id,
                # Command is used to create One2many and Many2many records.
                "line_ids": [
                    Command.create({
                        "name": record.name,
                        "quantity": 1,
                        "price_unit": (record.selling_price * 0.06),
                    }),
                    Command.create({
                        "name": "Administrative Fees",
                        "quantity": 1,
                        "price_unit": 100.00,
                    })
                ],
            })
        return res
