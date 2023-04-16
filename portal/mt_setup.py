from flask import Flask, Blueprint, current_app
from modern_treasury import ModernTreasury
from os import environ
import sqlite3

bp = Blueprint('setup', __name__)

modern_treasury = ModernTreasury(
    api_key=environ['API_KEY'],
    organization_id=environ['ORG_ID']
)


#region POST ledger things
def create_ledger():

    ledger = modern_treasury.ledgers.create(name = current_app.config['LEDGER_NAME'], metadata= { "name": current_app.config['LEDGER_NAME']})

    current_app.config['ledger'] = ledger

    print('Ledger created.')

#Todo Incomplete
# def create_global_customer_account_categories():
#     global_user_account_categories = dict()

#     for ac in current_app.config['']


def create_ledgers_accounts_with_bank_accounts():

    company_accounts = current_app.config['company_accounts'] if 'company_accounts' in current_app.config else dict()

    for account in current_app.config['COMPANY_LEDGER_ACCOUNTS_WITH_BANK_ACCOUNTS']:

        if(account['internal_account_id'] is None):
            pass

            #Todo autocreate IA incomplete

            # company_account_categories[account['name']] = modern_treasury.internal_accounts.create(
            #     connection_id=account['connection_id'],
            #     name=account['name'],
            #     party_name=account['party_name'],
            #     currency=account['currency']
            # )

        else:

            metadata = account['account_metadata']
            metadata['internal_account_id'] = account['internal_account_id']

            la = modern_treasury.ledger_accounts.create(
                name=account['name'],
                normal_balance='debit',
                currency=account['currency'],
                ledger_id=current_app.config['ledger'].id,
                metadata=metadata
            )

            company_accounts[account['name']] = la
            
    print('Ledger Account Categories for bank accounts created.')

    current_app.config['company_accounts'] = company_accounts

def create_account_categories_per_currency():

    company_account_categories = current_app.config['company_account_categories'] if 'company_account_categories' in current_app.config else dict()

    for currency in current_app.config['CURRENCIES']:
        for currency_lc in current_app.config['COMPANY_ACCOUNT_CATEGORIES_PER_CURRENCY']:

            metadata = currency_lc['metadata']
            metadata['currency'] = currency['currency']

            company_account_categories[currency['currency'] + ' - ' + currency_lc['name']] = modern_treasury.ledger_account_categories.create(
                name=currency['currency'] + ' - ' + currency_lc['name'],
                normal_balance='credit',
                ledger_id=current_app.config['ledger'].id,
                currency=currency['currency'],
                currency_exponent=currency['currency_exponent'] if currency['custom'] else None
                
            )

    print('Ledger Account Categories for currencies created.')

    current_app.config['company_account_categories'] = company_account_categories

def create_global_misc_accounts():

    company_accounts = current_app.config['company_accounts'] if 'company_accounts' in current_app.config else dict()

    for misc_account in current_app.config['COMPANY_MISC_ACCOUNTS_GLOBAL']:
        company_accounts[misc_account['name']] = modern_treasury.ledger_accounts.create(
            currency=misc_account['currency'],
            ledger_id=current_app.config['ledger'].id,
            name=misc_account['name'],
            normal_balance='debit',
            metadata=misc_account['metadata'],
            currency_exponent= misc_account['currency_exponent'] if 'currency_exponent' in misc_account else None
        )

    print('Global misc accounts created.')

    current_app.config['company_accounts'] = company_accounts

def create_misc_accounts_per_currency():

    company_accounts = current_app.config['company_accounts'] if 'company_accounts' in current_app.config else dict()

    for currency_la in current_app.config['COMPANY_MISC_ACCOUNTS_PER_CURRENCY']:
        for currency in current_app.config['CURRENCIES']:

            metadata = currency_la['metadata']
            metadata['currency'] = currency['currency']

            company_accounts[currency['currency'] + ' - ' + currency_la['name']] = modern_treasury.ledger_accounts.create(
                currency=currency['currency'],
                ledger_id=current_app.config['ledger'].id,
                name=currency['currency'] + ' - ' + currency_la['name'],
                normal_balance='debit',
                metadata=currency_la['metadata'],
                currency_exponent= currency['currency_exponent'] if currency['custom'] else None
            )

    print('Global misc accounts created.')

    current_app.config['company_accounts'] = company_accounts

#endregion POST ledger things

#region GET ledger things
def get_ledger():

    ledgers_with_that_name = modern_treasury.ledgers.list(metadata={"name": current_app.config['LEDGER_NAME']}).items

    try:
        current_app.config['ledger'] = ledgers_with_that_name[0]
        print('Existing ledger found.')
    except:
        raise Exception("Unable to find ledger.")
    
def get_ledgers_accounts_with_bank_accounts():

    company_accounts = current_app.config['company_accounts'] if 'company_accounts' in current_app.config else dict()

    for account in current_app.config['COMPANY_LEDGER_ACCOUNTS_WITH_BANK_ACCOUNTS']:

        company_accounts[account['name']] = modern_treasury.ledger_accounts.list(
                ledger_id=current_app.config['ledger'].id,
                metadata=account['account_metadata']
            ).items[0]

    if len(company_accounts) == len(current_app.config['COMPANY_LEDGER_ACCOUNTS_WITH_BANK_ACCOUNTS']):
        current_app.config['company_accounts'] = company_accounts
        print('Ledger Accounts for bank accounts found.')
    else:
        raise Exception("Unable to find LAs for bank accounts. Recommend deleting Ledger and recreating.")
    
def get_account_categories_per_currency():

    company_account_categories = current_app.config['company_account_categories'] if 'company_account_categories' in current_app.config else dict()

    starting_number_lcs =  len(company_account_categories)

    for currency in current_app.config['CURRENCIES']:
        for currency_lc in current_app.config['COMPANY_ACCOUNT_CATEGORIES_PER_CURRENCY']:

            metadata = currency_lc['metadata']
            metadata['currency'] = currency['currency']

            company_account_categories[currency['currency'] + ' - ' + currency_lc['name']] = modern_treasury.ledger_account_categories.list(
                ledger_id=current_app.config['ledger'].id,
                metadata=metadata
            )

    if len(company_account_categories) - starting_number_lcs == len(current_app.config['COMPANY_ACCOUNT_CATEGORIES_PER_CURRENCY']) * len(current_app.config['CURRENCIES']):
        current_app.config['company_account_categories'] = company_account_categories
        print('Ledger Account Categories per currency found.')
    else:
        raise Exception("Unable to find LACs per currency. Recommend deleting Ledger and recreating.")
    
def get_global_misc_accounts():

    company_accounts = current_app.config['company_accounts'] if 'company_accounts' in current_app.config else dict()

    starting_number_las =  len(company_accounts)

    for account in current_app.config['COMPANY_MISC_ACCOUNTS_GLOBAL']:

        company_accounts[account['name']] = modern_treasury.ledger_accounts.list(
            ledger_id=current_app.config['ledger'].id,
            metadata=account['metadata']
        ).items[0]

    if len(company_accounts) - starting_number_las == len(current_app.config['COMPANY_MISC_ACCOUNTS_GLOBAL']):
        current_app.config['company_accounts'] = company_accounts
        print('Global misc accounts found')
    else:
        raise Exception("Unable to find global misc accounts. Recommend deleting Ledger and recreating.")


def get_misc_accounts_per_currency():

    company_accounts = current_app.config['company_accounts'] if 'company_accounts' in current_app.config else dict()

    starting_number_las =  len(company_accounts)

    for currency_la in current_app.config['COMPANY_MISC_ACCOUNTS_PER_CURRENCY']:
        for currency in current_app.config['CURRENCIES']:

            metadata = currency_la['metadata']
            metadata['currency'] = currency['currency']

            company_accounts[currency['currency'] + ' - ' + currency_la['name']] = modern_treasury.ledger_accounts.list(
                ledger_id=current_app.config['ledger'].id,
                metadata=metadata
            ).items[0]

    print('Global misc accounts created.')

    current_app.config['company_accounts'] = company_accounts

    if len(company_accounts) - starting_number_las == len(current_app.config['COMPANY_ACCOUNT_CATEGORIES_PER_CURRENCY']) * len(current_app.config['CURRENCIES']):
        current_app.config['company_accounts'] = company_accounts
        print('Misc Ledger Accounts per currency found.')
    else:
        raise Exception("Unable to find LACs per currency. Recommend deleting Ledger and recreating.")
    
#endregion GET ledger things