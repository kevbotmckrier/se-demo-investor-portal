from modern_treasury import ModernTreasury
from dotenv import load_dotenv
import json
import os
import sys


# Load local .env file and assign org ID and key for auth
load_dotenv(verbose=True)
ORG_ID = os.environ.get("ORG_ID")
API_KEY = os.environ.get("API_KEY")

modern_treasury = ModernTreasury(
    api_key=API_KEY,
    organization_id=ORG_ID
)

with open("config.json", "r") as read_file:
    config_vars = json.load(read_file)

company_name = config_vars['COMPANY_NAME']

for oldLedger in modern_treasury.ledgers.list():
    if(company_name in oldLedger.name):
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