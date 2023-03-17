# se-demo-investor-portal

MT Sales Engineering demo investor portal to show how MT can integrate with any web app.

## Installation

```bash
pip install -r requirements.txt
```
## Credentials
The app can read in your credentials (org_id, api_key) from environment variables or from a `.env` file in the main directory. Here's a sample of what goes in the .env file:
```
ORG_ID=<INSERT_ORG_ID>
API_KEY=<INSERT_API_KEY>
```

## Usage
I recommend turning on debug mode to hot reload changes without having to restart the server. Run the following to enable:

```
export FLASK_DEBUG=1 
```

To run app as-is:
```python
flask run
```

## Customization
Use the `config.json` file to re-skin the app for a particular customer or use case. Simply update any of the values in the json file and they will be reflected throughout the app.

If you're comfortable with Python Flask, feel to add or modify routes in the main `app.py` file to add new pages or API calls. To add new pages, you'll need to define a new route, method, and likely a new template file to handle the display.

## Additional details
Built with:
1. [Python Flask](https://flask.palletsprojects.com/en/2.2.x/)
2. [Jinja templating engine](https://jinja.palletsprojects.com/en/3.1.x/)
2. [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
3. [Bootstrap icons](https://icons.getbootstrap.com/) - the app uses icon fonts
4. [Modern Treasury API](https://docs.moderntreasury.com/reference/getting-started)
