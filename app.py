from flask import Flask, render_template, abort, request, url_for, Response
from dotenv import load_dotenv
import os
import json
import requests

# Load local .env file and assign org ID and key for auth
load_dotenv(verbose=True)
ORG_ID = os.environ.get("ORG_ID")
API_KEY = os.environ.get("API_KEY")

#Pull in backend config values
distributions_start_date = os.environ.get("DISTRIBUTIONS_START_DATE")
distributions_end_date = os.environ.get("DISTRIBUTIONS_END_DATE")
payins_start_date = os.environ.get("PAYINS_START_DATE")
counterparty_id = os.environ.get("COUNTERPARTY_ID")
counterparty_id = os.environ.get("COUNTERPARTY_ID")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

@app.context_processor
def custom_values():
    return dict(
        company_name = app.config.get("COMPANY_NAME"),
        company_name_short = app.config.get("COMPANY_NAME_SHORT"),
        company_logo = app.config.get("COMPANY_LOGO"),
        username = app.config.get("USERNAME")
    )

@app.route('/')
@app.route('/index')
def index():

    return render_template('login.html')

@app.route('/login', methods= ['GET'])
def bain_login():
    
    return render_template('login.html', title="Login Page")


@app.route('/dashboard', methods= ['GET'])
def render_dashboard():

    return render_template('dashboard.html')


@app.route('/payments', methods= ['GET'])
def list_payments():
    params = {
        'type': 'wire',
        'counterparty_id': '574f75ea-5e22-430a-ab25-3bf7fa319e4a',
        'created_at_lower_bound': '2023-02-27'
        }
    data = list_expected_payments(ORG_ID, API_KEY, params=params)
    resp_status = data.status_code
    payments = data.json()
    payment_count = str(len(payments))
    pp_json = json.dumps(payments, indent=2)
    
    return render_template('payments.html', status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)


@app.route('/distributions')
def list_distributions():
    params = {
        'per_page': 25,
        'counterparty_id': '574f75ea-5e22-430a-ab25-3bf7fa319e4a',
        'effective_date_end': '2023-04-01',
        'effective_date_start': '2023-03-24'
    }
    data = list_payment_orders(ORG_ID, API_KEY, params=params)
    resp_status = data.status_code
    payments = data.json()
    payment_count = str(len(payments))
    pp_json = json.dumps(payments, indent=2)
    
    return render_template ('distributions.html', status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)


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


if __name__ == "__main__":
    app.run()