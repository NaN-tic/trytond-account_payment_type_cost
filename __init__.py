#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from invoice import *
from payment_type import *


def register():
    Pool.register(
        Invoice,
        PaymentType,
        module='account_payment_type_cost', type_='model')
