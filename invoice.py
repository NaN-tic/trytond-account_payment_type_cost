# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice']
__metaclass__ = PoolMeta


class Invoice:
    'Invoice'
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

        line = Line()
        line.invoice = self
        for key, value in Line.default_get(Line._fields.keys(),
                with_rec_name=False).iteritems():
            setattr(line, key, value)
        line.quantity = 1
        line.unit = None
        line.description = None
        line.product = self.payment_type.cost_product
        for key, value in line.on_change_product().iteritems():
            if 'rec_name' in key:
                continue
            setattr(line, key, value)
        line.unit_price = self.total_amount * self.payment_type.cost_percent
        return line
