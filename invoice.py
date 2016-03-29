# This file is part of account_payment_type_cost module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice']


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    def create_move(self):
        pool = Pool()
        Line = pool.get('account.invoice.line')
        if self.payment_type and self.payment_type.has_cost:
            lines = Line.search([
                    ('invoice', '=', self),
                    ('product', '=', self.payment_type.cost_product),
                    ])
            if not lines:
                line = self._get_payment_type_cost_line()
                line.save()
        # Taxes must be recomputed before creating the move
        self.update_taxes([self])
        return super(Invoice, self).create_move()

    def _get_payment_type_cost_line(self):
        " Returns invoice line with the cost"
        pool = Pool()
        Line = pool.get('account.invoice.line')

        if not self.payment_type or not self.payment_type.has_cost:
            return

        line = Line(**Line.default_get(Line._fields.keys()))
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
