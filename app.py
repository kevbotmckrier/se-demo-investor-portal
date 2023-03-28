from flask import Flask, render_template, abort, request, url_for, Response, session, redirect
from modern_treasury import ModernTreasury
import click

from dotenv import load_dotenv
from datetime import date

import os
import json
import requests
import random
import sys

# Load local .env file and assign org ID and key for auth
load_dotenv(verbose=True)
ORG_ID = os.environ.get("ORG_ID")
API_KEY = os.environ.get("API_KEY")

modern_treasury = ModernTreasury(
    api_key=API_KEY,
    organization_id=ORG_ID
)

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)


##########################
###  Config and setup  ###
##########################

#Let user pass in an existing ledger
@click.command()
@click.option('--ledger-id', help='Use existing ledger')
def load_ledger(ledger_id):
    ledger = modern_treasury.ledgers.retrieve(ledger_id)

#Otherwise, create a new Ledger on startup
if 'ledger' not in globals():
    ledger_name = app.config['COMPANY_NAME'] + ' - ' + date.today().isoformat()
    
    ##Check for existing ledgers
    ledgers_with_that_name = modern_treasury.ledgers.list(metadata={"name": ledger_name}).items
    if(len(ledgers_with_that_name) > 0):
        
        ledger = ledgers_with_that_name[0]
        uncategorized_cash_accounts = modern_treasury.ledger_accounts.list(ledger_id=ledger.id, metadata={'type': 'cash-account'})

        cash_accounts = dict()

        for cash_account in uncategorized_cash_accounts:
            cash_accounts[cash_account.metadata['bank']] = cash_account

    else:
        ledger = modern_treasury.ledgers.create(name = app.config['COMPANY_NAME'] + ' - ' + date.today().isoformat(), metadata= { "name": ledger_name})

        cash_accounts = dict()

        for cash_account in app.config['CUSTOMER_CASH_ACCOUNTS']:
            cash_accounts[cash_account['bank']] = modern_treasury.ledger_accounts.create(
                currency=cash_account['currency'],
                ledger_id=ledger.id,
                name=cash_account['vendor'] + ' - ' + cash_account['bank'],
                normal_balance='debit',
                metadata= {
                    'type': 'cash-account',
                    'bank': cash_account['bank']
                    }
            )

app.secret_key = ledger.id

@app.context_processor
def custom_values():
    return dict(
        company_name = app.config["COMPANY_NAME"],
        company_name_short = app.config["COMPANY_NAME_SHORT"],
        company_logo = app.config["COMPANY_LOGO"],
        user_attributes = app.config["USER_ATTRIBUTES"],
        product_attributes = app.config['PRODUCT_ATTRIBUTES'],
        customer_noun = app.config['CUSTOMER_NOUN'],
        pages_available = app.config['PAGES_AVAILABLE'],
        items_available_for_sale_collective_noun = app.config['ITEMS_FOR_SALE_COLLECTIVE_NOUN'],
        items_available_for_purchase = app.config['ITEMS_AVAILABLE_FOR_PURCHASE']
    )

@app.route('/signup')
def signup():
    session.clear()

    return signup_page()

@app.route('/login')
def login():
    return login_page()


@app.route('/dashboard', methods= ['GET'])
def render_dashboard():

    return render_template('dashboard.jinja')

@app.route('/ledger-dashboard', methods=['POST'])
def create_user():
    if 'email' in session:
        user_ledger_info = retrieve_user_ledger_info(session['email'])
        if(len(user_ledger_info['user_ledger_accounts'].items) > 0):

            return render_template('ledger-dashboard.jinja', 
                ledger_account_categories=user_ledger_info['user_ledger_account_categories'].items,
                ledger_accounts=user_ledger_info['user_ledger_accounts'].items,
                usd_balance = user_ledger_info['user_usd_balance'].items[0],
                )
        
        return render_template('ledger-dashboard.jinja')
    elif 'email' in request.form:
        session['email'] = request.form['email']
        session['human_name'] = request.form['human_name']
        session['state'] = request.form['state']
        user_ledger_info = retrieve_user_ledger_info(session['email'])
        if(len(user_ledger_info['user_ledger_accounts'].items) > 0):

            return render_template('ledger-dashboard.jinja', 
                ledger_account_categories=user_ledger_info['user_ledger_account_categories'].items,
                ledger_accounts=user_ledger_info['user_ledger_accounts'].items,
                usd_balance = user_ledger_info['user_usd_balance'].items[0],
                )
        else:
            for attribute in app.config["USER_ATTRIBUTES"]:
                session[attribute['var_name']] = request.form[attribute['var_name']]

            user_ledger_account_categories = []

            for lc in app.config['USER_ACCOUNT_CATEGORIES']:

                metadata = lc['metadata']
                for attribute in app.config["USER_ATTRIBUTES"]:
                    if attribute['add_to_metadata']:
                        metadata[attribute['var_name']] = request.form[attribute['var_name']]

            createdLc = modern_treasury.ledger_account_categories.create(
                name=lc['name'],
                normal_balance=lc['normal_balance'],
                currency=lc['currency'],
                ledger_id=ledger.id
            )

            user_ledger_account_categories.append(createdLc)
            
            user_ledger_accounts = []

            for la in app.config['USER_LEDGER_ACCOUNTS']:

                metadata = la['metadata']
                for attribute in app.config["USER_ATTRIBUTES"]:
                    if attribute['add_to_metadata']:
                        metadata[attribute['var_name']] = request.form[attribute['var_name']]
                
                createdLa = modern_treasury.ledger_accounts.create(
                    name=la['name'],
                    normal_balance=la['normal_balance'],
                    currency=la['currency'],
                    ledger_id=ledger.id,
                    metadata=la['metadata'],
                    currency_exponent= la['currency_exponent'] if 'currency_exponent' in la else None
                    )
                
                if(la['metadata']['name'] == 'usd-balance'):
                    user_usd_balance = createdLa
            
                user_ledger_accounts.append(createdLa)

            return render_template('ledger-dashboard.jinja', 
                ledger_account_categories=user_ledger_account_categories,
                ledger_accounts=user_ledger_accounts,
                usd_balance = user_usd_balance,
                )
    else:
        return redirect('/signup', code=307)

@app.route('/ledger-dashboard', methods=['GET'])
def load_dash():
    if 'email' in session:

        user_ledger_info = retrieve_user_ledger_info(session['email'])

        return render_template('ledger-dashboard.jinja', 
            ledger_account_categories=user_ledger_info['user_ledger_account_categories'].items,
            ledger_accounts=user_ledger_info['user_ledger_accounts'].items,
            usd_balance = user_ledger_info['user_usd_balance'].items[0],
            )
    else:
        return redirect('/signup', code=307)

@app.route('/payments', methods= ['GET'])
def list_payments():
    params = {
        'type': 'wire',
        'counterparty_id': app.config['COUNTERPARTY_ID'],
        'created_at_lower_bound': app.config['PAYINS_START_DATE']
        }
    data = list_expected_payments(ORG_ID, API_KEY, params=params)
    resp_status = data.status_code
    payments = data.json()
    payment_count = str(len(payments))
    pp_json = json.dumps(payments, indent=2)
    
    return render_template('payments.jinja', status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)


@app.route('/distributions')
def list_distributions():
    params = {
        'per_page': 25,
        'counterparty_id': '574f75ea-5e22-430a-ab25-3bf7fa319e4a',
        'effective_date_end': app.config['DISTRIBUTIONS_END_DATE'],
        'effective_date_start': app.config['DISTRIBUTIONS_START_DATE']
    }
    data = list_payment_orders(ORG_ID, API_KEY, params=params)
    resp_status = data.status_code
    payments = data.json()
    payment_count = str(len(payments))
    pp_json = json.dumps(payments, indent=2)
    
    return render_template ('distributions.jinja', status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)

@app.route('/bank-deposit')
def bank_deposit_page():

    bank_accounts = modern_treasury.counterparties.list(metadata={ "email": session['email']}).items[0].accounts
    return render_template('bank-deposit.jinja', bank_accounts=bank_accounts)

@app.route('/new-bank-deposit', methods=['GET','POST'])
def create_bank_deposit():

    payment_order = modern_treasury.payment_orders.create(
        amount=int(request.form['amount']),
        direction='debit',
        originating_account_id=app.config['ORIGINATING_ACCOUNT_ID'],
        type="ach",
        receiving_account_id=request.form['bank-account'],
        priority="high" if request.form['payment-method'] == 'same-day-ach' else "normal",
        description=f"Deposit from bank account via {request.form['payment-method']} on " + date.today().strftime('%x'),
        ledger_transaction=construct_deposit_ledger_transaction(
            bank='jpm',
            amount=request.form['amount'],
            email=session['email'],
            description=f"Deposit from bank account via {request.form['payment-method']} on " + date.today().strftime('%x'),
            metadata={'user': session['email']}
            )
    )

    return render_template('new-bank-deposit.jinja', deposit_info=payment_order)

@app.route('/ledger-transactions', methods=['GET'])
def view_ledger_transactions():

    ledger_transactions = modern_treasury.ledger_transactions.list(metadata={
        'user': session['email']
    })

    print(ledger_transactions.items)
    print(ledger_transactions.items[0].description)

    return render_template('ledger-transactions.jinja', ledger_transactions=ledger_transactions.items)

@app.route('/purchase', methods=['GET'])
def purchase_investments():

    items_available_for_purchase = app.config['ITEMS_AVAILABLE_FOR_PURCHASE']
    user_ledger_accounts = retrieve_user_ledger_info(session['email'])

    for item in items_available_for_purchase:
        print((random.randrange(-100 * item['variation_percent'],100* item['variation_percent']))/100)
        item['current_price_in_usd_cents'] = round(item['price_in_usd'] + item['price_in_usd'] * ((random.randrange(-100 * item['variation_percent'],100* item['variation_percent']))/10000),0)
        item['current_price_in_usd_dollars_formatted'] = '${:,.2f}'.format(item['current_price_in_usd_cents']/100)

    return render_template('purchase.jinja', items_available_for_purchase=items_available_for_purchase, user_ledger_accounts=user_ledger_accounts)

@app.post('/make-purchase')
def make_purchase():
    print(request.json)
    return("test complete")

@app.route('/')
@app.route('/index')
def use_configured_default():

    if 'email' in session:
        return redirect(app.config['DETAULT_DASHBOARD_PATH'],307)

    if(app.config['DEFAULT_ENTRY_POINT'] == "signup"):
        return signup_page()
    elif(app.config['DEFAULT_ENTRY_POINT'] == "login"):
        return login_page()
    else:
        return signup_page()

#### Re-used renders
def login_page():
    return render_template('login.jinja', title=f"{app.config['COMPANY_NAME']} - Login Page")

def signup_page():
    return render_template('signup.jinja', title=f"{app.config['COMPANY_NAME']} - Signup Page")


# NON-ROUTE METHODS BELOW


def create_payment_order(payload, org_id, api_key):
    url = 'https://app.moderntreasury.com/api/payment_orders'
    try:
        resp = requests.post(url=url, auth=(org_id, api_key), json=payload)
        return resp
    except Exception as e:
        print(e)
        return "Call failed."


def async_create_po(payload, org_id, api_key):
    url = "https://app.moderntreasury.com/api/payment_orders/create_async"
    try:
        response = requests.post(url=url, auth=(org_id, api_key), json=payload)
        return response
    except Exception as e:
        print(e)
        return "Call failed."


def create_po(payload, org_id, api_key):
    url = "https://app.moderntreasury.com/api/payment_orders"
    try:
        response = requests.post(url=url, auth=(org_id, api_key), json=payload)
        return response
    except Exception as e:
        print(e)
        return "Call failed."


def create_ep_from_form(payload, org_id, api_key):
    url = 'https://app.moderntreasury.com/api/expected_payments'
    try:
        resp = requests.post(url=url, auth=(org_id, api_key), json=payload)
        return resp
    except Exception as e:
        print(e)
        return "Call failed."


def create_va(payload, org_id, api_key):
    url = "https://app.moderntreasury.com/api/virtual_accounts"
    try:
        resp = requests.post(url=url, auth=(org_id, api_key), json=payload)
        return resp
    except Exception as e:
        print(e)
        return "Call failed."


def list_expected_payments(org_id, api_key, params=None):
    url = 'https://app.moderntreasury.com/api/expected_payments'
    try:
        resp = requests.get(url, auth=(org_id, api_key), params=params)
        return resp
    except Exception as e:
        print(e)
        return "Call failed."


def list_payment_orders(org_id, api_key, params=None):
    url = 'https://app.moderntreasury.com/api/payment_orders'
    try:
        resp = requests.get(url, auth=(org_id, api_key), params=params)
        return resp
    except Exception as e:
        print(e)
        return "Call failed."


def dollars_to_cents(dollars):
    cents = float(dollars) * 100

    return int(cents)

################################################
###         MT Interaction functions        ####
################################################


def retrieve_user_usd_balance(email):

    metadata_filters = {
        'email': email,
        'name': 'usd-balance'
    }
    
    return modern_treasury.ledger_accounts.list(metadata=metadata_filters)

def construct_deposit_ledger_transaction(bank, amount, email, metadata, description):

    user_balance_la_id = retrieve_user_usd_balance(email).items[0].id

    cash_account_id = cash_accounts[bank].id

    metadata['user_visible_accounts'] = user_balance_la_id
    metadata[user_balance_la_id] = "USD Balance"

    ledger_entries = [
        { 
            "amount": int(amount),
            "direction": "debit",
            "ledger_account_id": cash_account_id
        },
        { 
            "amount": int(amount),
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

def retrieve_user_ledger_info(email):
            
    metadata_filters = {
        'email': email
    }

    user_usd_balance = modern_treasury.ledger_accounts.list(metadata=metadata_filters | { "name": "usd-balance"})
    user_btc_balance = modern_treasury.ledger_accounts.list(metadata=metadata_filters | { "name": "btc-balance"})
    user_eth_balance = modern_treasury.ledger_accounts.list(metadata=metadata_filters | { "name": "eth-balance"})

    user_ledger_accounts = modern_treasury.ledger_accounts.list(metadata=metadata_filters)
    user_ledger_account_categories = modern_treasury.ledger_account_categories.list(metadata=metadata_filters)

    return({ 
        "user_usd_balance": user_usd_balance,
        "user_btc_balance":user_btc_balance,
        "user_eth_balance": user_eth_balance,
        "user_ledger_accounts": user_ledger_accounts,
        "user_ledger_account_categories": user_ledger_account_categories,
        })

if __name__ == "__main__":
    app.run()