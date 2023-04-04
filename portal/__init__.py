import os
import json
from dotenv import load_dotenv

from flask import Flask

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_file('config.json', load=json.load)


    ## Setup ledgers
    with app.app_context():
        from .setup_ledgers import create_ledger, get_ledger, create_cash_accounts, get_cash_accounts, init_app, get_other_accounts, create_other_accounts
        init_app(app)

        try:
            get_ledger()
        except Exception as e:
            print(e)
            try:
                create_ledger()
                create_cash_accounts()
                create_other_accounts()
            except Exception as e:
                print(e)
                print("Setup failure.")
        try:
            get_cash_accounts()
            get_other_accounts()
        except Exception as e:
            print(e)
            print("Setup failure.")

    app.secret_key =  app.config['ledger'].id

    from . import auth
    from . import investment_firm
    from . import ledger_dashboard

    app.register_blueprint(auth.bp)
    app.register_blueprint(investment_firm.bp)
    app.register_blueprint(ledger_dashboard.bp)

    @app.context_processor
    def custom_values():
        return dict(
            company_name = app.config["COMPANY_NAME"],
            company_name_short = app.config["COMPANY_NAME_SHORT"],
            company_logo = app.config["COMPANY_LOGO"],
            user_attributes = app.config["USER_ATTRIBUTES"],
            product_attributes = app.config['PRODUCT_ATTRIBUTES'],
            customer_noun = app.config['CUSTOMER_NOUN'],
            pages_available = app.config['PAGES_AVAILABLE'],
            items_available_for_sale_collective_noun = app.config['ITEMS_FOR_SALE_COLLECTIVE_NOUN'],
            items_available_for_purchase = app.config['ITEMS_AVAILABLE_FOR_PURCHASE'],
            default_dashboard_path = app.config['DEFAULT_DASHBOARD_PATH']
        )

    return app