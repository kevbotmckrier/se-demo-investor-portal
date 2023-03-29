from flask import Flask, render_template, abort, request, url_for, Response, session, redirect, Blueprint, current_app, g
from modern_treasury import ModernTreasury
from os import environ
from datetime import date
import random
from portal.auth import authed
from portal.mt_interactions import load_ledgers, load_bank_accounts, create_ledger_accounts, load_ledger_transactions

bp = Blueprint('ledger_dashboard', __name__)

modern_treasury = ModernTreasury(
    api_key=environ['API_KEY'],
    organization_id=environ['ORG_ID']
)

@bp.route('/ledger-dashboard', methods=['POST'])
@authed
@create_ledger_accounts
@load_ledgers
def create_accounts_and_load_dash():
            
        return render_template('ledger-dashboard.jinja', 
            ledger_account_categories=g.user_ledger_account_categories.items,
            ledger_accounts=g.user_ledger_accounts.items,
            usd_balance=g.user_usd_balance.items[0],
            )

@bp.route('/ledger-dashboard', methods=['GET'])
@authed
@load_ledgers
def load_dash():
            
        return render_template('ledger-dashboard.jinja', 
            ledger_account_categories=g.user_ledger_account_categories.items,
            ledger_accounts=g.user_ledger_accounts.items,
            usd_balance=g.user_usd_balance.items[0],
            )

@bp.route('/bank-deposit')
@authed
@load_bank_accounts
def bank_deposit_page():

    return render_template('bank-deposit.jinja', bank_accounts=g.bank_accounts)

@bp.route('/new-bank-deposit', methods=['GET','POST'])
@authed
@load_ledgers
def create_bank_deposit():

    payment_order =  modern_treasury.payment_orders.create(
        amount=int(request.form['amount'])*100,
        direction='debit',
        originating_account_id=current_app.config['ORIGINATING_ACCOUNT_ID'],
        type="ach",
        receiving_account_id=request.form['bank-account'],
        priority="high" if request.form['payment-method'] == 'same-day-ach' else "normal",
        description=f"Deposit from bank account via {request.form['payment-method']} on " + date.today().strftime('%x'),
        ledger_transaction=construct_deposit_ledger_transaction(
            bank='jpm',
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

    print(g.ledger_transactions.items)

    return render_template('ledger-transactions.jinja', ledger_transactions=g.ledger_transactions.items)

@bp.route('/purchase', methods=['GET'])
@authed
@load_ledgers
def purchase_investments():

    items_available_for_purchase = current_app.config['ITEMS_AVAILABLE_FOR_PURCHASE']

    for item in items_available_for_purchase:
        print((random.randrange(-100 * item['variation_percent'],100* item['variation_percent']))/100)
        item['current_price_in_usd_cents'] = round(item['price_in_usd'] + item['price_in_usd'] * ((random.randrange(-100 * item['variation_percent'],100* item['variation_percent']))/10000),0)
        item['current_price_in_usd_dollars_formatted'] = '${:,.2f}'.format(item['current_price_in_usd_cents']/100)

    return render_template('purchase.jinja',
        items_available_for_purchase=items_available_for_purchase, 
        user_ledger_accounts= {
            'user_usd_balance': g.user_usd_balance,
            'user_btc_balance': g.user_btc_balance,
            'user_eth_balance': g.user_eth_balance,
        })

@bp.post('/make-purchase')
@authed
def make_purchase():
    print(request.form)
    return Response({"test":"test"}, status=201)

def construct_deposit_ledger_transaction(bank, amount, email, metadata, description):

    user_balance_la_id = g.user_usd_balance.items[0].id

    cash_account_id = current_app.config['cash_accounts'][bank].id

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