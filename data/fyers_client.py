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

# session = fyersModel.SessionModel(
#     client_id=client_id,
#     secret_key=secret_key,
#     redirect_uri=redirect_uri,
#     response_type=response_type,
#     grant_type=grant_type
# )
#
# ## Generate the access token using the authorization code
# generatedTokenUtl = session.generate_authcode()
# webbrowser.open(generatedTokenUtl, new=1)
#
# ## printing the url received
# print(generatedTokenUtl)
#
# webbrowser.open(generatedTokenUtl, new=1)
#
# auth_token = input("enter the auth token")
# session.set_token(auth_token)
# response = session.generate_token()
# print(response)
# print(response["access_token"])
#
def get_fyers_client():
    config = configparser.ConfigParser()
    config.read("fyers.ini")

    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIl0sImF0X2hhc2giOiJnQUFBQUFCcFpFbXFiQXJHdHdVU0pmYVZMWkR0N0J6TXlNMlJpLW5lZlViN3gxaU5mSDI1UnpwUGlpUFFRV3NfOXZPUC00SGpJWk1FcWNPcnZBRUxsZkJtZHRNZG5COVFwQlVYa1VYVXl6RTZ6VF91VmNzRlhSUT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJiM2I3ZjhiYjRjNzBjNmFjYzU4NmUyMDcyMTE4ZDk0NzM2N2RkYjAxMjhlNDdiOThjYmM2NjQyYyIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWUE0NjE3NiIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzY4MjY0MjAwLCJpYXQiOjE3NjgxODAxMzgsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc2ODE4MDEzOCwic3ViIjoiYWNjZXNzX3Rva2VuIn0.umMj3SaNg9r94ZyXqVsW7l1Gl0omu1tRupK8LRl1wk4"
    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        is_async=False,
        log_path="logs/"
    )
    return fyers
