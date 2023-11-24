import pandas as pd
import gspread
import json
import datetime
from oauth2client.client import OAuth2Credentials
from oauth2client.service_account import ServiceAccountCredentials
#from streamlit_gsheets import GSheetsConnection
from gspread_pandas import Spread, Client
from google.oauth2 import service_account
import streamlit as st


def load_the_spreadsheet(sh, spreadsheetname):
    
    worksheet = sh.worksheet(spreadsheetname)
    df = pd.DataFrame(worksheet.get_all_records())
    
    return df




def gsheet_conn():
    #conn = st.experimental_connection("gsheets", type=GSheetsConnection)
    #df = conn.read(worksheet="CLIENTE", spreadsheet='https://docs.google.com/spreadsheets/d/1ZYE380SOilw4aG9K61xIc6W23411yhmIAqyA9YKJiO8/')
    #st.dataframe(df)

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"], scopes = scope)

    client = Client(scope=scope,creds=credentials)
    spreadsheetname = "datos"
#    spread = Spread(spreadsheetname,client = client)

    sh = client.open(spreadsheetname)

    return sh

    # Check the connection
    #st.write(spread.url)
