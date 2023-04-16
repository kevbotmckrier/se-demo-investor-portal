from flask import Flask, render_template, abort, request, url_for, Response, session, redirect, Blueprint, current_app, g
from modern_treasury import ModernTreasury
from os import environ
from datetime import date
import random
from portal.auth import authed
from portal.mt_interactions import load_user_ledger_accounts_and_categories, load_ledger_transactions, create_user_ledger_accounts_and_categories, load_bank_accounts

bp = Blueprint('ledger_dashboard', __name__)

modern_treasury = ModernTreasury(
    api_key=environ['API_KEY'],
    organization_id=environ['ORG_ID']
)

@bp.route('/ledger-dashboard', methods=['POST'])
@authed
@create_user_ledger_accounts_and_categories
# @load_user_ledger_info
def create_accounts_and_load_dash():
            
        return render_template('ledger-dashboard.jinja',
            ledger_account_categories=g.user_ledger_account_categories.values(),
            ledger_accounts=g.user_ledger_accounts.values(),
            visible_currencies=current_app.config['CURRENCIES_ON_DASHBOARD']
        )

@bp.route('/ledger-dashboard', methods=['GET'])
@authed
@load_user_ledger_accounts_and_categories
def load_dash():

        return render_template('ledger-dashboard.jinja', 
            ledger_account_categories=g.user_ledger_account_categories.values(),
            ledger_accounts=g.user_ledger_accounts.values(),
            visible_currencies=current_app.config['CURRENCIES_ON_DASHBOARD']
        )

@bp.route('/bank-deposit')
@authed
@load_bank_accounts
def bank_deposit_page():

    return render_template('bank-deposit.jinja', bank_accounts=g.bank_accounts)

@bp.route('/new-bank-deposit', methods=['GET','POST'])
@authed
@load_user_ledger_accounts_and_categories
def create_bank_deposit():

    payment_order =  modern_treasury.payment_orders.create(
        amount=str(int(request.form['amount'])*100),
        direction='debit',
        originating_account_id=current_app.config['ORIGINATING_ACCOUNT_ID'],
        type="ach",
        receiving_account_id=request.form['bank-account'],
        priority="high" if request.form['payment-method'] == 'same-day-ach' else "normal",
        description=f"Deposit from bank account via {request.form['payment-method']} on " + date.today().strftime('%x'),
        ledger_transaction=construct_deposit_ledger_transaction(
            bank='SB' + str(random.randint(1,3)),
            amount=(int(request.form['amount'])*100),
            email=session['email'],
            description=f"Deposit from bank account via {request.form['payment-method']} on " + date.today().strftime('%x'),
            metadata={'user': session['email']}
            )
    )

    return render_template('new-bank-deposit.jinja', deposit_info=payment_order)

@bp.route('/ledger-transactions', methods=['GET'])
@authed
@load_ledger_transactions
def view_ledger_transactions():

    return render_template('ledger-transactions.jinja', ledger_transactions=g.ledger_transactions.items, la_names=g.la_names)

@bp.route('/purchase', methods=['GET'])
@authed
@load_user_ledger_accounts_and_categories
def purchase_investments():

    items_available_for_purchase = current_app.config['CURRENCIES']

    for item in items_available_for_purchase:

        item['current_price_in_usd_cents'] = round(item['price_in_usd'] + item['price_in_usd'] * ((random.randrange(-100 * item['variation_percent'],100* item['variation_percent']))/10000),0) // 100 * 100
        item['current_price_in_usd_dollars_formatted'] = '${:,.2f}'.format(item['current_price_in_usd_cents']/100)

    return render_template('purchase.jinja',
        items_available_for_purchase=items_available_for_purchase, 
        user_ledger_accounts=g.user_ledger_accounts,
        user_ledger_account_categories=g.user_ledger_account_categories
    )

@bp.post('/make-purchase')
@load_user_ledger_accounts_and_categories
def make_purchase():
    
    amount = request.form['amount']
    item = request.form['item']
    price = request.form['current_price']

    lt = modern_treasury.ledger_transactions.create(
        effective_date= str(date.today().isoformat()),
        status='posted', 
        ledger_entries=construct_purchase_ledger_transaction(
            item= item,
            price= price,
            amount= amount,
            description=f'Purchasing {amount} of {item} at {price}'
        ),
    )

    return('Purchase made successfully', 201)


## Helper functions
def construct_deposit_ledger_transaction(bank, amount, email, metadata, description):

    user_deposit_account_metadata = {
         'currency': current_app.config['BASE_CURRENCY'],
         'type': 'user-balance',
         'sub-type': 'unrestricted'
    }

    company_deposit_account_metadata = {
                "type": "company-balance",
                "subtype": "bank-account"
    }

    for la in g.user_ledger_accounts:
        if user_deposit_account_metadata.items() <= la.metadata.items():
             user_balance_la_id = la.id

    cash_accounts = list()

    for la_key in current_app.config['company_accounts']:
         if company_deposit_account_metadata.items() <= current_app.config['company_accounts'][la_key].metadata.items():
              cash_accounts.append(current_app.config['company_accounts'][la_key])

    selected_cash_account_id = random.choice(cash_accounts).id

    metadata['user_visible_accounts'] = user_balance_la_id
    metadata[user_balance_la_id] = "USD Balance"

    ledger_entries = [
        { 
            "amount": str(amount),
            "direction": "debit",
            "ledger_account_id": selected_cash_account_id
        },
        { 
            "amount": str(amount),
            "direction": "credit",
            "ledger_account_id": user_balance_la_id
        }
    ]

    ledger_transaction = {
        'ledger_entries': ledger_entries,
        'metadata': metadata
    }
    
    if description:
        ledger_transaction['description'] = description

    return(ledger_transaction)

def construct_purchase_ledger_transaction(item, price, amount, description):

    user_balance_ids = dict()
    net_purchase_ids = dict()

    for currency in current_app.config['CURRENCIES']:
         
         user_balance_ids[currency['currency']] = g.user_ledger_accounts[currency['currency'] + ' - General Balance'].id

         net_purchase_ids[currency['currency']] = current_app.config['company_accounts'][currency['currency'] + ' - Net Purchases'].id

    price = int(float(price) // 1)

    metadata = dict()
    metadata['user_visible_accounts'] = ''

    for currency in user_balance_ids:
        metadata['user_visible_accounts'] += user_balance_ids[currency]

    ledger_entries = [
        { 
            "amount": str(int(amount) * int(price)),
            "direction": "debit",
            "ledger_account_id": user_balance_ids['USD']
        },
        { 
            "amount": str(int(amount) * int(price)),
            "direction": "credit",
            "ledger_account_id": net_purchase_ids['USD']
        },
                { 
            "amount": str(amount),
            "direction": "credit",
            "ledger_account_id": user_balance_ids[item]
        },
        { 
            "amount": str(amount),
            "direction": "debit",
            "ledger_account_id": net_purchase_ids[item]
        }
    ]

    ledger_transaction = {
        'ledger_entries': ledger_entries,
        'metadata': metadata
    }
    
    if description:
        ledger_transaction['description'] = description

    return(ledger_entries)


