from flask import Flask, render_template, abort, request, url_for, Response
from dotenv import load_dotenv
import os
import json
import requests

# Load local .env file and assign org ID and key for auth
load_dotenv(verbose=True)
KKMT_ORG_ID = os.environ.get("KKMT_ORG_ID")
KKMT_API_KEY = os.environ.get("KKMT_API_KEY")

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():

    return render_template('bain-login.html', title='Bain Login')

@app.route('/bain/login', methods= ['GET'])
def bain_login():
    
    return render_template('bain-login.html', title="Bain Login")


@app.route('/bain/dashboard', methods= ['GET'])
def bain_render_dash():
    user = {'username': 'John'}
    
    return render_template('bain-dashboard.html', user=user)


@app.route('/bain/payments', methods= ['GET'])
def bain_show_payments():
    user = {'username': 'John'}
    data = list_expected_payments(KKMT_ORG_ID, KKMT_API_KEY)
    url = 'https://app.moderntreasury.com/api/expected_payments?type=wire&counterparty_id=12c199b2-2f8e-46e3-866d-8bdf97cc317f&created_at_lower_bound=2023-02-27'
    try:
        data = requests.get(url, auth=(KKMT_ORG_ID, KKMT_API_KEY))
        resp_status = data.status_code
        payments = data.json()
        payment_count = str(len(payments))
        pp_json = json.dumps(payments, indent=2)
    except Exception as e:
        print(e)
        return "Call failed."
    
    return render_template('bain-payments.html', user=user, status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)


@app.route('/bain/distributions')
def bain_list_distributions():
    user = {'username': 'John'}
    url = 'https://app.moderntreasury.com/api/payment_orders?per_page=25&counterparty_id=12c199b2-2f8e-46e3-866d-8bdf97cc317f&effective_date_end=2023-03-01'
    try:
        data = requests.get(url, auth=(KKMT_ORG_ID, KKMT_API_KEY))
        resp_status = data.status_code
        payments = data.json()
        payment_count = str(len(payments))
        pp_json = json.dumps(payments, indent=2)
    except Exception as e:
        print(e)
        return "Call failed."
    
    return render_template ('bain-distributions.html', user=user, status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)


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


def list_expected_payments(org_id, api_key):
    url = 'https://app.moderntreasury.com/api/expected_payments'
    try:
        resp = requests.get(url, auth=(org_id, api_key))
        return resp
    except Exception as e:
        print(e)
        return "Call failed."


def dollars_to_cents(dollars):
    cents = float(dollars) * 100

    return int(cents)


if __name__ == "__main__":
    app.run()