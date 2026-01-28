from fyers_apiv3 import fyersModel
import configparser
import webbrowser
import logging

logger = logging.getLogger(__name__)

# Define your Fyers API credentials
client_id = "8H9U4T74P7-100"  # Replace with your client ID
secret_key = "IH1QWI9W06"  # Replace with your secret key
redirect_uri = "https://www.google.com"  # Replace with your redirect URI
response_type = "code"
state = "sample_State"
grant_type = "authorization_code"

def get_fyers_token():
    logger.info("Generating Fyers token...")
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )

    ## Generate the access token using the authorization code
    generatedTokenUtl = session.generate_authcode()
    logger.info(f"Please go to this URL to generate an auth token: {generatedTokenUtl}")

    webbrowser.open(generatedTokenUtl, new=1)
    ## printing the url received
    print(generatedTokenUtl)

    webbrowser.open(generatedTokenUtl, new=1)
    logger.info(f"Please go to this URL to generate an auth token: {generatedTokenUtl}")

    # In a real application, you would need a way to get the auth token back from the user.
    # For this script, we will log a message and assume the token is provided manually.
    logger.info("Please provide the auth token manually.")

    auth_token = input("enter the auth token:")
    session.set_token(auth_token)
    response = session.generate_token()
    print(response)
    print("access_token")
    print(response["access_token"])
    print("refresh_token")
    print(response["refresh_token"])

def get_fyers_client():
    logger.info("Initializing Fyers client...")
    config = configparser.ConfigParser()
    config.read("fyers.ini")

    logger.info("TODO: Using hardcoded access token. This is not recommended for production.")
    #TODO
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIl0sImF0X2hhc2giOiJnQUFBQUFCcGVWVlRiSktPVC1BU1U3TzN6UE9ETnZQSjN3SURGdC1tMFZVSTBPbkxaZU02V2c3aEV2TGlZSHJPcTc1eEVidHpoQUxKRG5qZGFGcjRsSlZGUXo5UEVKN3VTQm9NV1VqcG5mbU0tRXVoQmFQOFhlVT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJhZmVmZGRjNzIxMWY5OGZlYTJhMzQwM2E5NjM5YmIyOWZkNzZkNDdiOGIzZmY0ZDRiMDRiZTlmNiIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWUE0NjE3NiIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzY5NjQ2NjAwLCJpYXQiOjE3Njk1NTkzNzksImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc2OTU1OTM3OSwic3ViIjoiYWNjZXNzX3Rva2VuIn0.LopLxExp59svF0oNyn2Ms7dzHXSkYGUaP7-fBx2CGIM"
    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        is_async=False,
        log_path="logs/"
    )
    logger.debug("Fyers client initialized successfully.")
    return fyers


# get_fyers_token()