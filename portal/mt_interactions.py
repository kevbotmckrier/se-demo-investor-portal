from flask import Flask, render_template, abort, request, url_for, Response, session, redirect, Blueprint, current_app, g
from modern_treasury import ModernTreasury
from os import environ
from datetime import date
import random
from portal.auth import authed
from functools import wraps

bp = Blueprint('load_mt_data', __name__)

modern_treasury = ModernTreasury(
    api_key=environ['API_KEY'],
    organization_id=environ['ORG_ID']
)

def load_ledgers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            metadata_filters = {
                'email': session['email']
            }

            g.user_usd_balance =  modern_treasury.ledger_accounts.list(
                metadata=metadata_filters | { "name": "usd-balance"},
                ledger_id=current_app.config['ledger'].id,
                )
            
            g.user_btc_balance =  modern_treasury.ledger_accounts.list(
                metadata=metadata_filters | { "name": "btc-balance"},
                ledger_id=current_app.config['ledger'].id,
                )
            
            g.user_eth_balance =  modern_treasury.ledger_accounts.list(
                metadata=metadata_filters | { "name": "eth-balance"},
                ledger_id=current_app.config['ledger'].id,
                )

            g.user_ledger_accounts =  modern_treasury.ledger_accounts.list(
                metadata=metadata_filters,
                ledger_id=current_app.config['ledger'].id,
                )
            
            g.user_ledger_account_categories =  modern_treasury.ledger_account_categories.list(
                metadata=metadata_filters,
                ledger_id=current_app.config['ledger'].id,
                )
        return f(*args, **kwargs)
    return decorated_function

def load_bank_accounts(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            metadata_filters = {
                'email': session['email']
            }

            counterparty =  modern_treasury.counterparties.list(metadata={ "email": session['email']})
            g.bank_accounts = counterparty.items[0].accounts
        return f(*args, **kwargs)
    return decorated_function

def create_ledger_accounts(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        g.user_ledger_accounts =  modern_treasury.ledger_accounts.list(
            metadata={
                'email': request.form
            },
            ledger_id=current_app.config['ledger'].id,
            )
        
        if(len(g.user_ledger_accounts.items) == 0):

            for attribute in current_app.config["USER_ATTRIBUTES"]:
                session[attribute['var_name']] = request.form[attribute['var_name']]

            for lc in current_app.config['USER_ACCOUNT_CATEGORIES']:

                metadata = lc['metadata']
                for attribute in current_app.config["USER_ATTRIBUTES"]:
                    if attribute['add_to_metadata']:
                        metadata[attribute['var_name']] = request.form[attribute['var_name']]

                modern_treasury.ledger_account_categories.create(
                    name=lc['name'],
                    normal_balance=lc['normal_balance'],
                    currency=lc['currency'],
                    ledger_id=current_app.config['ledger'].id
                    )

            for la in current_app.config['USER_LEDGER_ACCOUNTS']:

                metadata = la['metadata']
                for attribute in current_app.config["USER_ATTRIBUTES"]:
                    if attribute['add_to_metadata']:
                        metadata[attribute['var_name']] = request.form[attribute['var_name']]
                
                modern_treasury.ledger_accounts.create(
                    name=la['name'],
                    normal_balance=la['normal_balance'],
                    currency=la['currency'],
                    ledger_id=current_app.config['ledger'].id,
                    metadata=la['metadata'],
                    currency_exponent= la['currency_exponent'] if 'currency_exponent' in la else None
                    )
        return f(*args, **kwargs)
    return decorated_function

def load_ledger_transactions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            metadata_filters = {
                'user': session['email']
            }

            g.ledger_transactions =  modern_treasury.ledger_transactions.list(
                ledger_id=current_app.config['ledger'].id,
                metadata=metadata_filters
                )
            
            print(metadata_filters)
            print(current_app.config['ledger'].id)
            
        return f(*args, **kwargs)
    return decorated_function