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

def load_user_ledger_accounts_and_categories(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            metadata_filters = {
                'email': session['email']
            }

            user_ledger_account_categories =  modern_treasury.ledger_account_categories.list(
                metadata=metadata_filters,
                ledger_id=current_app.config['ledger'].id
            ).items

            g.user_ledger_account_categories = dict()
            for lc in user_ledger_account_categories:

                g.user_ledger_account_categories[lc.name] = lc
            
            user_ledger_accounts = modern_treasury.ledger_accounts.list(
                metadata=metadata_filters,
                ledger_id=current_app.config['ledger'].id
            ).items

            g.user_ledger_accounts = dict()
            for la in user_ledger_accounts:
                g.user_ledger_accounts[la.name] = la

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

def create_user_ledger_accounts_and_categories(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        #Create account categories per currency
        user_ledger_account_categories = g.user_ledger_account_categories if 'user_ledger_account_categories' in g else dict()

        for currency_lc in current_app.config['USER_ACCOUNT_CATEGORIES_PER_CURRENCY']:
            for currency in current_app.config['CURRENCIES']:

                name = currency['currency'] + ' - ' + currency_lc['name']

                metadata = currency_lc['metadata']
                metadata['currency'] = currency['currency']
                metadata = add_user_attributes_to_metadata(metadata)

                user_ledger_account_categories[name] = modern_treasury.ledger_account_categories.create(
                    name=name,
                    currency=currency['currency'],
                    ledger_id=current_app.config['ledger'].id,
                    currency_exponent= currency['currency_exponent'] if 'currency_exponent' in currency else None,
                    normal_balance='credit',
                    metadata=metadata
                )

        g.user_ledger_account_categories = user_ledger_account_categories

        # Create per currency accounts
        user_ledger_accounts = g.user_ledger_accounts if 'user_ledger_accounts' in g else dict()

        for currency_la in current_app.config['USER_LEDGER_ACCOUNTS_PER_CURRENCY']:
            for currency in current_app.config['CURRENCIES']:

                name = currency['currency'] + ' - ' + currency_la['name']

                metadata = currency_la['metadata']
                metadata['currency'] = currency['currency']
                metadata = add_user_attributes_to_metadata(metadata)

                user_ledger_accounts[name] = modern_treasury.ledger_accounts.create(
                    name=name,
                    currency=currency['currency'],
                    ledger_id=current_app.config['ledger'].id,
                    currency_exponent= currency['currency_exponent'] if 'currency_exponent' in currency else None,
                    normal_balance='credit',
                    metadata=metadata
                )

                # Add LAs to LCs
                for lc_to_add_to in currency_la['categories']:
                    for lc_name in user_ledger_account_categories:

                        metadata_filter = lc_to_add_to['metadata']
                        metadata_filter['currency'] = currency['currency']

                        if(metadata_filter.items() <= user_ledger_account_categories[lc_name].metadata.items()):
                            modern_treasury.ledger_account_categories.add_ledger_account(
                                id=user_ledger_account_categories[lc_name].id,
                                ledger_account_id=user_ledger_accounts[name].id
                            )
                            break

        g.user_ledger_accounts = user_ledger_accounts

        ### User globals not currently used/implemented

        # todo 
        # Create global account categories
        # for global_lc in current_app.config['USER_ACCOUNT_CATEGORIES_GLOBAL']:
            #todo currency implemented

        # todo 
        # Create global ledger accounts

        return f(*args, **kwargs)
    return decorated_function

def load_ledger_transactions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session:
            # metadata_filters = {
            #     'user': session['email']
            # }
            metadata_filters = { "User_Id":"58926379"}

            g.ledger_transactions =  modern_treasury.ledger_transactions.list(
                ledger_id=current_app.config['ledger'].id,
                metadata=metadata_filters
                )
            
            all_ledger_accounts = modern_treasury.ledger_accounts.list(ledger_id=current_app.config['ledger'].id)

            la_names = dict()

            for la in all_ledger_accounts:
                la_names[la.id] = la.name

            g.la_names = la_names
            
        return f(*args, **kwargs)
    return decorated_function

def add_user_attributes_to_metadata(metadata):

    for attribute in current_app.config["USER_ATTRIBUTES"]:
        if attribute['add_to_metadata']:
            metadata[attribute['var_name']] = request.form[attribute['var_name']]

    return metadata