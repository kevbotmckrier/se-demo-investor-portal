from flask import Flask, Blueprint, current_app
from modern_treasury import ModernTreasury
from os import environ
import click
import sys
from datetime import date

bp = Blueprint('setup', __name__)

modern_treasury = ModernTreasury(
    api_key=environ['API_KEY'],
    organization_id=environ['ORG_ID']
)

ledger_name = current_app.config['COMPANY_NAME'] + ' - ' + date.today().isoformat()
print('Ledger name is ' + ledger_name)

def create_ledger():

    ledger = modern_treasury.ledgers.create(name = ledger_name, metadata= { "name": ledger_name})

    current_app.config['ledger'] = ledger

    print('Ledger created.')

    return True


def create_cash_accounts():
    cash_accounts = dict()

    for cash_account in current_app.config['CUSTOMER_CASH_ACCOUNTS']:
        cash_accounts[cash_account['bank']] = modern_treasury.ledger_accounts.create(
            currency=cash_account['currency'],
            ledger_id=current_app.config['ledger'].id,
            name=cash_account['vendor'] + ' - ' + cash_account['bank'],
            normal_balance='debit',
            metadata= {
                'type': 'cash-account',
                'bank': cash_account['bank']
                }
        )
    
    if len(cash_accounts) == len(current_app.config['CUSTOMER_CASH_ACCOUNTS']):
        current_app.config['cash_accounts'] = cash_accounts
        print('Ledger cash accounts created.')
        return True

    elif len(cash_accounts) > 0:
        raise Exception("Partial creation. Recommend delete and recreate.")
    else:
        raise Exception("Unable to create cash accounts.")

def get_ledger():

    ledgers_with_that_name = modern_treasury.ledgers.list(metadata={"name": ledger_name}).items

    try:
        current_app.config['ledger'] = ledgers_with_that_name[0]
        print('Existing ledger found.')
        return True
    except:
        raise Exception("Unable to find ledger.")
    
def get_cash_accounts():

    cash_accounts = dict()

    for cash_account in current_app.config['CUSTOMER_CASH_ACCOUNTS']:
        cash_accounts[cash_account['bank']] = modern_treasury.ledger_accounts.create(
            currency=cash_account['currency'],
            ledger_id=current_app.config['ledger'].id,
            name=cash_account['vendor'] + ' - ' + cash_account['bank'],
            normal_balance='debit',
            metadata= {
                'type': 'cash-account',
                'bank': cash_account['bank']
                }
        )

    if len(cash_accounts) == len(current_app.config['CUSTOMER_CASH_ACCOUNTS']):
        current_app.config['cash_accounts'] = cash_accounts
        print('Existing cash accounts found.')
        return True
    elif len(cash_accounts) > 0:
        raise Exception("Partial creation. Recommend deleting Ledger and recreating.")
    else:
        raise Exception("Unable to find any cash accounts. Recommend deleting Ledger and recreating.")
    

def delete_ledgers():

    for oldLedger in modern_treasury.ledgers.list():
        if(current_app.config['COMPANY_NAME'] in oldLedger.name):
            sys.stdout.write(oldLedger.name + 'might be a duplicate, delete? (y/n)')
            choice = input().lower()
            if choice == 'y':
                try:
                    modern_treasury.ledgers.delete(oldLedger.id)
                except:
                    "Huh, didn't take"
                else:
                    'Deleted'
            elif choice == 'n':
                sys.stdout.write('Ok')
            else:
                sys.stdout.write("That wasn't an option, but we're just going to move on.")
    
@click.command('delete-ledgers')
def delete_ledgers_command():
    """Delete ledgers matching the chosen company name."""

    delete_ledgers()

@click.command('create-ledger')
def create_ledger_command():
    """Setup ledger ahead of time. Use with caution, may cause issues duplicate ledgers."""

@click.command('create-cash-accounts')
def create_cash_accounts_command():
    """Setup ledger ahead of time. Use with caution, may cause issues duplicate ledgers."""

    create_cash_accounts()

def init_app(app):
    app.cli.add_command(delete_ledgers_command)