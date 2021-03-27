# This file is part of account_payment_type_cost module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    @classmethod
    def set_number(cls, invoices):
        Line = Pool().get('account.invoice.line')

        to_create, update_tax = [], []
        for invoice in invoices:
            if invoice.payment_type and invoice.payment_type.has_cost:
                lines = Line.search([
                        ('invoice', '=', invoice),
                        ('product', '=', invoice.payment_type.cost_product),
                        ])
                if not lines:
                    line = invoice._get_payment_type_cost_line()
                    if line:
                        to_create.append(line._save_values)
                        update_tax.append(invoice)
        if to_create:
            Line.create(to_create)
        # Taxes must be recomputed before creating the move
        if update_tax:
            cls.update_taxes(update_tax)
        return super(Invoice, cls).set_number(invoices)

    def _get_payment_type_cost_line(self):
        " Returns invoice line with the cost"
        pool = Pool()
        Line = pool.get('account.invoice.line')

        if not self.payment_type or not self.payment_type.has_cost:
            return

        line = Line()
        line.invoice = self
        line.quantity = 1
        line.unit = None
        line.description = None
        line.product = self.payment_type.cost_product
        line.on_change_product()
        if self.payment_type.compute_over_total_amount:
            line.unit_price = (self.total_amount *
                self.payment_type.cost_percent)
        else:
            line.unit_price = (self.untaxed_amount *
                self.payment_type.cost_percent)
        return line
