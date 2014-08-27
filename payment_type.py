# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond import backend
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Not
from trytond.transaction import Transaction

__all__ = ['PaymentType']
__metaclass__ = PoolMeta


class PaymentType:
    __name__ = 'account.payment.type'

    has_cost = fields.Boolean('Has Costs?', help="Check it if it has to "
        "create a line with the operation cost in the customer invoices.")
    cost_product = fields.Many2One('product.product', 'Cost product', states={
            'required': Eval('has_cost', False),
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])
    cost_percent = fields.Numeric('Cost (%)', digits=(8, 4), states={
            'required': Eval('has_cost', False),
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().cursor

        # Migration from 3.2.0: removed constraint
        table = TableHandler(cursor, cls, module_name)
        table.drop_constraint('cost_percent')
