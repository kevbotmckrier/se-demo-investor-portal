from flask import Flask, Blueprint, current_app
from modern_treasury import ModernTreasury
from os import environ
import click
from datetime import date
import sys
import portal.mt_setup as setup
import traceback

modern_treasury = ModernTreasury(
    api_key=environ['API_KEY'],
    organization_id=environ['ORG_ID']
)

bp = Blueprint('admin', __name__)

@bp.cli.group('ledgers', short_help="CRUD ledgers commands")
def admin():
    """Admin"""
    pass

@admin.command('delete')
@click.option('-s', '--skip-confirm', 'skip_confirmation', is_flag=True, show_default=True, default=False, help="Confirm before deleting ledgers.")
def delete_ledgers(skip_confirmation):
    """Deletes existing ledgers"""

    #Loop through all ledgers
    for oldLedger in modern_treasury.ledgers.list():

        #If name matches pattern
        if(current_app.config['COMPANY_NAME'] in oldLedger.name):

            if(not skip_confirmation):
                sys.stdout.write(oldLedger.name + 'might be a duplicate, delete? (y/n)\n')
                choice = input().lower()
                if choice == 'y':
                    try:
                        modern_treasury.ledgers.delete(oldLedger.id)
                    except:
                        sys.stdout.write("Huh, didn't take\n")
                    else:
                        sys.stdout.write('Deleted\n')
                elif choice == 'n':
                    sys.stdout.write('Ok, next\n')
                else:
                    sys.stdout.write("That wasn't an option, but we're just going to move on.\n")
            else:
                try:
                    sys.stdout.write(f"Deleting {oldLedger.name}...\n")
                    modern_treasury.ledgers.delete(oldLedger.id)
                except:
                    sys.stdout.write("Huh, didn't take\n")
                else:
                    sys.stdout.write('Deleted\n')

@admin.command('setup')
def setup_ledgers():
    """Creates Ledger, Ledger Accounts, and Ledger Account Categories based on config"""

    try:
        setup.create_ledger()
    except:
        print("Unable to create Ledger, exiting.")
        exit()

    try:
        setup.create_ledgers_accounts_with_bank_accounts()
    except:
        print("Unable to create Leder Account Categories for Bank Accounts, exiting.")
        print(traceback.format_exc())
        exit()
    
    try:
        setup.create_account_categories_per_currency()
    except:
        print("Unable to create Leder Account Categories for Currencies, exiting.")
        print(traceback.format_exc())
        exit()

    try:
        setup.create_global_misc_accounts()
    except:
        print("Unable to create misc Ledger Accounts, exiting.")
        print(traceback.format_exc())
        exit()

    try:
        setup.create_misc_accounts_per_currency()
    except:
        print("Unable to create misc Ledger Accounts per currency, exiting.")
        print(traceback.format_exc())
        exit()

    print("Ledger setup complete.")
    
    ## Function not defined yet, config category unused

    # try:
    #     setup.create_global_customer_account_categories()
    # except:
    #     print("Unable to create global account categories, exiting.")
    #     print(traceback.format_exc())
    #     exit()