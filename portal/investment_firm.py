from flask import Flask, render_template, abort, request, url_for, Response, session, redirect, Blueprint, current_app
from modern_treasury import AsyncModernTreasury
from os import environ
import json

from datetime import date
from .helper_functions import list_expected_payments, list_payment_orders
from .auth import authed

bp = Blueprint('investment_firm', __name__)

API_KEY=environ['API_KEY'],
ORG_ID=environ['ORG_ID']

@bp.route('/dashboard', methods= ['GET'])
# @login_required
def render_dashboard():

    return render_template('dashboard.jinja')

@bp.route('/payments', methods= ['GET'])
# @login_required
def list_payments():
    params = {
        'type': 'wire',
        'counterparty_id': current_app.config['COUNTERPARTY_ID'],
        'created_at_lower_bound': current_app.config['PAYINS_START_DATE']
        }
    data = list_expected_payments(ORG_ID, API_KEY, params=params)
    resp_status = data.status_code
    payments = data.json()
    payment_count = str(len(payments))
    pp_json = json.dumps(payments, indent=2)
    
    return render_template('payments.jinja', status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)


@bp.route('/distributions')
# @login_required
def list_distributions():
    params = {
        'per_page': 25,
        'counterparty_id': '574f75ea-5e22-430a-ab25-3bf7fa319e4a',
        'effective_date_end': current_app.config['DISTRIBUTIONS_END_DATE'],
        'effective_date_start': current_app.config['DISTRIBUTIONS_START_DATE']
    }
    data = list_payment_orders(ORG_ID, API_KEY, params=params)
    resp_status = data.status_code
    payments = data.json()
    payment_count = str(len(payments))
    pp_json = json.dumps(payments, indent=2)
    
    return render_template ('distributions.jinja', status_code=resp_status, response_json=pp_json, payment_count=payment_count, payments=payments)