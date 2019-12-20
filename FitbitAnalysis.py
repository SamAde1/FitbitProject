import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
import datetime

CLIENT_ID = "22B9YV"
CLIENT_SECRET = "ef1c8462955073dfd83d7a457e6af480"

server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

#Auth Client
auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN,
                             refresh_token=REFRESH_TOKEN, system="en_GB")

yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
today = str(datetime.datetime.now().strftime("%Y%m%d"))

fit_statsSTEPS = auth2_client.intraday_time_series('activities/steps', 
                                                base_date=yesterday2)

print(fit_statsSTEPS)

#https://towardsdatascience.com/collect-your-own-fitbit-data-with-python-ff145fa10873
#https://www.freecodecamp.org/news/how-i-analyzed-the-data-from-my-fitbit-to-improve-my-overall-health-a2e36426d8f9/
