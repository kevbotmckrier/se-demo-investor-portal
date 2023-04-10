import os
import json
from dotenv import load_dotenv
from datetime import date
from flask.cli import AppGroup
from flask import Flask
import traceback

def create_app(config_filename='config.json'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    app.config.from_file(config_filename, load=json.load)
    app.config['LEDGER_NAME'] = app.config['COMPANY_NAME'] + ' - ' + date.today().isoformat()

    # Custom Commands
    from portal import admin
    app.register_blueprint(admin.bp)

    # Setup ledgers
    from portal import mt_setup
    if(app.debug == True):

        with app.app_context():
            
            try:
                mt_setup.get_ledger()
                mt_setup.get_account_categories_with_bank_accounts()
                mt_setup.get_account_categories_per_currency()
                mt_setup.get_global_misc_accounts()
                mt_setup.get_misc_accounts_per_currency()
                
                app.secret_key =  app.config['ledger'].id
                    
            except:
                print('Unable to find necessary ledger components.')
                print(traceback.format_exc())
                exit()

            


        



    # Import application blueprints
    from portal import auth
    from portal import investment_firm
    from portal import ledger_dashboard

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
            items_available_for_purchase = app.config['CURRENCIES'],
            default_dashboard_path = app.config['DEFAULT_DASHBOARD_PATH']
        )

    return app