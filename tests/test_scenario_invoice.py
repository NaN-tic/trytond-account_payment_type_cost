import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear, create_tax,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install account_payment_type_cost Module
        activate_modules('account_payment_type_cost')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Create party
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.customer_taxes.append(tax)
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'service'
        template.list_price = Decimal('40')
        template.cost_price = Decimal('25')
        template.account_category = account_category
        product, = template.products
        product.cost_price = Decimal('25')
        template.save()
        product, = template.products
        cost_product = Product()
        cost_template = ProductTemplate()
        cost_template.name = 'cost product'
        cost_template.default_uom = unit
        cost_template.type = 'service'
        cost_template.list_price = Decimal('40')
        cost_template.account_category = account_category
        cost_product, = cost_template.products
        cost_product.cost_price = Decimal('25')
        cost_template.save()
        cost_product, = cost_template.products

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()

        # Create payment types
        PaymentType = Model.get('account.payment.type')
        payment_type_no_cost = PaymentType()
        payment_type_no_cost.name = 'No cost'
        payment_type_no_cost.kind = 'both'
        payment_type_no_cost.save()
        payment_type_cost = PaymentType()
        payment_type_cost.name = 'Cost'
        payment_type_cost.kind = 'both'
        payment_type_cost.has_cost = True
        payment_type_cost.cost_product = cost_product
        payment_type_cost.cost_percent = Decimal('0.05')
        payment_type_cost.save()

        # Create invoice without cost
        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice(type='out')
        invoice.party = party
        invoice.payment_term = payment_term
        invoice.payment_type = payment_type_no_cost
        line = InvoiceLine()
        invoice.lines.append(line)
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40.0')
        invoice.save()
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(len(invoice.lines), 1)

        # Create invoice with cost
        invoice2 = Invoice(type='out')
        invoice2.party = party
        line = InvoiceLine()
        invoice2.lines.append(line)
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40.0')
        invoice2.save()
        invoice2.payment_term = payment_term
        invoice2.payment_type = payment_type_cost
        invoice2.save()
        invoice2.click('post')
        self.assertEqual(invoice2.state, 'posted')
        line1, line2 = invoice2.lines
        self.assertEqual(line1.amount, Decimal('200.00'))
        self.assertEqual(line2.amount, Decimal('10.00'))
