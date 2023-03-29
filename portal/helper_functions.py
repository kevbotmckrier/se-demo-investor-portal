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