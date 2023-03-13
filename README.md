# se-demo-investor-portal

MT Sales Engineering demo investor portal to show how MT can integrate with any web app.

## Installation

```bash
pip install -r requirements.txt
```
## Credentials
The app is built to read in your credentials (org_id, api_key) from a `.env` file in the main directory. Here's a sample of what goes in the .env file:
```
ORG_ID=<INSERT_ORG_ID>
API_KEY=<INSERT_API_KEY>
```
Make sure to add the `.env` file to `.gitignore` to ensure you don't commit it.

## Usage

To run app as-is:
```python
flask run
```
Feel free to add or modify routes in the main app.py file. You customize the look and feel by adding new logos in the /static directory and calling them in the appropriate template files.

## Additional details
Built with:
1. [Python Flask](https://flask.palletsprojects.com/en/2.2.x/)
2. [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
3. [Bootstrap icons](https://icons.getbootstrap.com/) - the app uses icon fonts
4. [Modern Treasury API](https://docs.moderntreasury.com/reference/getting-started)
