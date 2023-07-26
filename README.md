# se-demo-investor-portal

MT Sales Engineering demo investor portal to show how MT can easily integrate with web applications to power more real-time reporting around money movement. The app in this repo is deployed at: https://demo-investor-portal.onrender.com/login

## Installation

```bash
pip install -r requirements.txt
```
## Setup

### Credentials
The app can read in your credentials (org_id, api_key) from environment variables or from a `.env` file in the main directory. Here's a sample of what goes in the .env file:
```
ORG_ID=<INSERT_ORG_ID>
API_KEY=<INSERT_API_KEY>
```
### MT Objects

The config.json file will read in some Modern Treasury objects directly. Command line instructions will create other necessary objects on your behalf.

The `COMPANY_LEDGER_ACCOUNTS_WITH_BANK_ACCOUNTS` requires an `internal_account_id`. Creation of new internal account via the connection_id parameter is not fully implemented yet.

When a user signs up they will supply an email address. The app will query MT for counterparties with that email address and retrieve their bank accounts to make deposits. You will need to create a counterparty with the correct email address ahead of time OR hardcode the email address in the `load_bank_accounts` function in the `mt_interactions.py` file.

To create the ledger and associated objects run `flask admin ledgers setup`. `flask admin --help` will provide guidance as to various objects. These objects will be loaded when you start the application.

## Usage
I recommend turning on debug mode to hot reload changes without having to restart the server. Run the following to enable:

To run app as-is:
```python
flask --debug run
```

## Customization
Use the `config.json` file to re-skin the app for a particular customer or use case. Simply update any of the values in the json file and they will be reflected throughout the app.

In addition to naming and visual customization the ledger structure, user attributes captured, items available for purchase, and pages visible are also defined in the `config.json` file.

### Simple Customizations

`PAGES_AVAILABLE` determines what's available on the nav.

`USER_ATTRIBUTES` controls signup form.

> :warning: Removing `email` will break portions of the demo!

`CURRENCIES_ON_DASHBOARD` controls what Ledger Account currencies are loaded on the home page.

### Structural Cutomizations

`CURRENCIES` defines the currencies used in the demo. These should almost always retain USD with the `base_currency` property set to `true`.

`USER_LEDGER_ACCOUNTS_GLOBAL`, `USER_LEDGER_ACCOUNTS_PER_CURRENCY`, `USER_ACCOUNT_CATEGORIES_GLOBAL`, `USER_ACCOUNT_CATEGORIES_PER_CURRENCY`, `COMPANY_ACCOUNT_CATEGORIES_GLOBAL`, `COMPANY_MISC_ACCOUNTS_PER_CURRENCY`, `COMPANY_ACCOUNT_CATEGORIES_PER_CURRENCY`, `COMPANY_LEDGER_ACCOUNTS_WITH_BANK_ACCOUNTS`, and `COMPANY_MISC_ACCOUNTS_GLOBAL` sections control the structure of the ledger. User parameters marked `GLOBAL` will create one account or category for each user. Company parameters marked `GLOBAL` will create one account or category. `PER_CURRENCY` parameters will create accounts or categories for each currency. These sections will also define what accounts are added to which categories.

### Additional Changes

If you're comfortable with Python Flask, feel to add or modify routes in the main `app.py` file to add new pages or API calls. To add new pages, you'll need to define a new route, method, and likely a new template file to handle the display.

## Additional details
Built with:
1. [Python Flask](https://flask.palletsprojects.com/en/2.2.x/)
2. [Jinja templating engine](https://jinja.palletsprojects.com/en/3.1.x/)
2. [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
3. [Bootstrap icons](https://icons.getbootstrap.com/) - the app uses icon fonts
4. [Modern Treasury API](https://docs.moderntreasury.com/reference/getting-started)
5. [Modern Treasury Python SDK](https://github.com/Modern-Treasury/modern-treasury-python)
