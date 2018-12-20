================
Invoice Scenario
================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Install account_payment_type_cost Module::

    >>> config = activate_modules('account_payment_type_cost')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create tax::

    >>> Tax = Model.get('account.tax')
    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.customer_taxes.append(tax)
    >>> product, = template.products
    >>> product.cost_price = Decimal('25')
    >>> template.save()
    >>> product, = template.products
    >>> cost_product = Product()
    >>> cost_template = ProductTemplate()
    >>> cost_template.name = 'cost product'
    >>> cost_template.default_uom = unit
    >>> cost_template.type = 'service'
    >>> cost_template.list_price = Decimal('40')
    >>> cost_template.account_expense = expense
    >>> cost_template.account_revenue = revenue
    >>> cost_template.customer_taxes.append(Tax(tax.id))
    >>> cost_product, = cost_template.products
    >>> cost_product.cost_price = Decimal('25')
    >>> cost_template.save()
    >>> cost_product, = cost_template.products

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create payment types::

    >>> PaymentType = Model.get('account.payment.type')
    >>> payment_type_no_cost = PaymentType()
    >>> payment_type_no_cost.name = 'No cost'
    >>> payment_type_no_cost.kind = 'both'
    >>> payment_type_no_cost.save()
    >>> payment_type_cost = PaymentType()
    >>> payment_type_cost.name = 'Cost'
    >>> payment_type_cost.kind = 'both'
    >>> payment_type_cost.has_cost = True
    >>> payment_type_cost.cost_product = cost_product
    >>> payment_type_cost.cost_percent = Decimal('0.05')
    >>> payment_type_cost.save()

Create invoice without cost::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.payment_type = payment_type_no_cost
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('40.0')
    >>> invoice.save()
    >>> invoice.click('post')
    >>> invoice.state
    u'posted'
    >>> len(invoice.lines)
    1

Create invoice with cost::

    >>> invoice2 = Invoice()
    >>> invoice2.party = party
    >>> line = InvoiceLine()
    >>> invoice2.lines.append(line)
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('40.0')
    >>> invoice2.save()
    >>> invoice2.payment_term = payment_term
    >>> invoice2.payment_type = payment_type_cost
    >>> invoice2.save()
    >>> invoice2.click('post')
    >>> invoice2.state
    u'posted'
    >>> invoice2.reload()
    >>> line1, line2 = invoice2.lines
    >>> line1.amount
    Decimal('200.00')
    >>> line2.amount
    Decimal('10.00')
