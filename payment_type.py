# This file is part of account_payment_type_cost module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond import backend
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Not


class PaymentType(metaclass=PoolMeta):
    __name__ = 'account.payment.type'

    has_cost = fields.Boolean('Has Costs?', help="Check it if it has to "
        "create a line with the operation cost in the customer invoices.")
    cost_product = fields.Many2One('product.product', 'Cost product',
        domain=[
            ('type', '=', 'service'),
            ],
        states={
            'required': Eval('has_cost', False),
            'invisible': Not(Eval('has_cost', False)),
            },
        context={
            'company': Eval('company', -1),
            },
        depends=['has_cost', 'company'])
    cost_percent = fields.Numeric('Cost (%)', digits=(8, 4), states={
            'required': Eval('has_cost', False),
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])
    compute_over_total_amount = fields.Boolean('Compute over total amount',
        help='Check it if you want to compute cost over total amount with tax,'
        ' otherwise will compute it over total amount without tax', states={
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])

    @classmethod
    def __register__(cls, module_name):
        super(PaymentType, cls).__register__(module_name)

        # Migration from 3.2.0: removed constraint
        table = backend.TableHandler(cls, module_name)
        table.drop_constraint('cost_percent')
