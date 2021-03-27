#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import payment_type

def register():
    Pool.register(
        invoice.Invoice,
        payment_type.PaymentType,
        module='account_payment_type_cost', type_='model')
