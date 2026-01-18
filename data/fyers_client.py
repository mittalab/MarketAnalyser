from fyers_apiv3 import fyersModel
import configparser
import webbrowser

# Define your Fyers API credentials
client_id = "8H9U4T74P7-100"  # Replace with your client ID
secret_key = "IH1QWI9W06"  # Replace with your secret key
redirect_uri = "https://www.google.com"  # Replace with your redirect URI
response_type = "code"
state = "sample_State"
grant_type = "authorization_code"

def get_fyers_token():
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )

    ## Generate the access token using the authorization code
    generatedTokenUtl = session.generate_authcode()
    webbrowser.open(generatedTokenUtl, new=1)

    ## printing the url received
    print(generatedTokenUtl)

    webbrowser.open(generatedTokenUtl, new=1)

    auth_token = input("enter the auth token:")
    session.set_token(auth_token)
    response = session.generate_token()
    print(response)
    print("access_token")
    print(response["access_token"])
    print("refresh_token")
    print(response["refresh_token"])

def get_fyers_client():
    config = configparser.ConfigParser()
    config.read("fyers.ini")

    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIl0sImF0X2hhc2giOiJnQUFBQUFCcGJJQnNjVkJpS256VUdYU1psNVNzb0ZLZE9oMkVuUVlVNFhrWi1NU1YtSXplcDdUczY5Vi1rcVNTcHR0OGZ3dF9tS3VQT09sM3pYMTUyOWFHUG9Gd25Od2hLaS1YWVRtcHFMSmRZRlBYWmZ6azhOST0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJkNjQyMDhjOGI0YjczZDQxODZhMWQyYjk0YzM2MzFmZGJjYzQxMjVlZjU2YWE4YzFlNjE1ODBiMyIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWUE0NjE3NiIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzY4NzgyNjAwLCJpYXQiOjE3Njg3MTg0NDQsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc2ODcxODQ0NCwic3ViIjoiYWNjZXNzX3Rva2VuIn0.duYqs7kHpiO7GoJX7V2R8d2e3BQY6GjebnzWwZeHRuk"
    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        is_async=False,
        log_path="logs/"
    )
    return fyers


# get_fyers_token()